"""
Migrate all data from hosted PostgreSQL (source) to Neon (target).

Reads SOURCE_DB_* from env for source, DATABASE_URL for target.
Excludes django_migrations so target keeps its migration state.
Preserves primary keys and FKs by copying in dependency order.
When source/target schemas differ (e.g. farms_croptype, farms_farm),
copies only shared columns (intersection) including "id".

Usage:
  python migrate_data_hosted_to_neon.py [--dry-run] [--truncate-only] [--sequences-only]

  Set in .env:
    SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_NAME, SOURCE_DB_USER, SOURCE_DB_PASSWORD
    DATABASE_URL (target Neon)
"""
from __future__ import annotations

import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path

# Load .env
if (Path(__file__).resolve().parent / ".env.local").exists():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env.local")
elif (Path(__file__).resolve().parent / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Tables we never copy (target keeps its own)
EXCLUDE_TABLES = {"django_migrations"}

# Optional: exclude sessions/admin log to avoid invalidating sessions
# EXCLUDE_TABLES = {"django_migrations", "django_session", "django_admin_log"}

BATCH_SIZE = 2000


def source_config():
    host = os.environ.get("SOURCE_DB_HOST", "dev-et.cropeye.ai").replace("https://", "").replace("http://", "").strip()
    return {
        "host": host,
        "port": os.environ.get("SOURCE_DB_PORT", "5432"),
        "dbname": os.environ.get("SOURCE_DB_NAME", "CROPDB_TEST"),
        "user": os.environ.get("SOURCE_DB_USER", "farm_management_l1wj_user"),
        "password": os.environ.get("SOURCE_DB_PASSWORD", "DySO3fcTFjb8Rgp9IZIxGYgLZ7KxwmjL"),
    }


def target_config():
    url = os.environ.get("DATABASE_URL")
    if not url or not url.startswith("postgresql"):
        raise SystemExit("DATABASE_URL (postgresql://...) not set. Set it to your Neon connection string.")
    return url


def get_public_tables(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        return [r[0] for r in cur.fetchall()]


def get_fk_deps(conn) -> list[tuple[str, str]]:
    """Return (child_table, parent_table) for each FK."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                tc.table_name AS child,
                ccu.table_name AS parent
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
              AND ccu.table_schema = 'public'
              AND tc.table_name <> ccu.table_name;
        """)
        return [(r[0], r[1]) for r in cur.fetchall()]


def topological_order(tables: list[str], deps: list[tuple[str, str]]) -> list[str]:
    """Order tables so parents come before children. Uses Kahn's algorithm."""
    parents = defaultdict(set)
    children = defaultdict(set)
    for c, p in deps:
        if c in tables and p in tables:
            parents[c].add(p)
            children[p].add(c)

    in_degree = {t: len(parents[t]) for t in tables}
    queue = [t for t in tables if in_degree[t] == 0]
    result = []
    while queue:
        t = queue.pop(0)
        result.append(t)
        for c in children[t]:
            in_degree[c] -= 1
            if in_degree[c] == 0:
                queue.append(c)

    # Tables not in result (cyclic refs) go at end
    for t in tables:
        if t not in result:
            result.append(t)
    return result


def get_columns(conn, table: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table,))
        return [r[0] for r in cur.fetchall()]


def copy_table(
    source_conn,
    target_conn,
    table: str,
    cols: list[str],
    dry_run: bool,
) -> int:
    sc = source_conn.cursor()
    tc = target_conn.cursor()
    sc.execute(sql.SQL("SELECT {} FROM {}").format(
        sql.SQL(", ").join(map(sql.Identifier, cols)),
        sql.Identifier(table),
    ))
    rows = sc.fetchall()
    if not rows:
        return 0
    n = len(rows)
    if dry_run:
        return n
    cols_id = [sql.Identifier(c) for c in cols]
    insert = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
        sql.Identifier(table),
        sql.SQL(", ").join(cols_id),
    )
    insert_str = insert.as_string(tc)
    for i in range(0, n, BATCH_SIZE):
        chunk = rows[i : i + BATCH_SIZE]
        execute_values(tc, insert_str, chunk, page_size=BATCH_SIZE)
    return n


def _table_has_id_column(conn, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = 'id';
            """,
            (table,),
        )
        return cur.fetchone() is not None


def reset_sequences(conn, tables: list[str]):
    with conn.cursor() as cur:
        for table in tables:
            if not _table_has_id_column(conn, table):
                continue
            cur.execute(
                "SELECT pg_get_serial_sequence(%s, 'id')",
                (f"public.{table}",),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                continue
            seq = row[0]
            try:
                cur.execute(
                    sql.SQL("SELECT setval(%s::regclass, COALESCE((SELECT MAX(id) FROM {}), 1))").format(
                        sql.Identifier(table)
                    ),
                    (seq,),
                )
            except psycopg2.Error:
                pass


def main():
    ap = argparse.ArgumentParser(description="Migrate data from hosted DB to Neon")
    ap.add_argument("--dry-run", action="store_true", help="Only report row counts, do not copy")
    ap.add_argument("--truncate-only", action="store_true", help="Only truncate target tables, then exit")
    ap.add_argument("--sequences-only", action="store_true", help="Only reset sequences on target (no copy)")
    args = ap.parse_args()

    source_cfg = source_config()
    target_url = target_config()

    print("=" * 60)
    print("Data migration: Hosted PostgreSQL -> Neon")
    print("=" * 60)
    print(f"Source: {source_cfg['host']}:{source_cfg['port']} / {source_cfg['dbname']}")
    print(f"Target: (Neon from DATABASE_URL)")
    if args.dry_run:
        print("Mode: DRY RUN (no writes)")
    if args.truncate_only:
        print("Mode: TRUNCATE ONLY")
    if args.sequences_only:
        print("Mode: SEQUENCES ONLY")
    print()

    try:
        source_conn = psycopg2.connect(**source_cfg)
        source_conn.autocommit = False
    except psycopg2.Error as e:
        print(f"ERROR: Cannot connect to SOURCE DB: {e}")
        sys.exit(1)

    try:
        target_conn = psycopg2.connect(target_url)
        target_conn.autocommit = False
    except psycopg2.Error as e:
        print(f"ERROR: Cannot connect to TARGET (Neon) DB: {e}")
        source_conn.close()
        sys.exit(1)

    try:
        all_tables = [t for t in get_public_tables(source_conn) if t not in EXCLUDE_TABLES]
        deps = get_fk_deps(source_conn)
        order = topological_order(all_tables, deps)

        print(f"Tables to migrate: {len(order)} (excluded: {EXCLUDE_TABLES})")
        print()

        if args.truncate_only:
            print("Truncating target tables...")
            to_truncate = [t for t in order if t in get_public_tables(target_conn)]
            if to_truncate:
                with target_conn.cursor() as cur:
                    quoted = ", ".join(f'"{t}"' for t in to_truncate)
                    cur.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE;")
                target_conn.commit()
                print(f"Truncated {len(to_truncate)} tables.")
            else:
                print("No matching tables found on target.")
            return

        if args.sequences_only:
            print("Resetting sequences on target...")
            target_tables = [t for t in get_public_tables(target_conn) if t not in EXCLUDE_TABLES]
            reset_sequences(target_conn, target_tables)
            target_conn.commit()
            print("Done.")
            return

        # Truncate target tables (excluding django_migrations)
        target_tables = [t for t in order if t in get_public_tables(target_conn)]
        if not target_tables:
            print("No matching tables on target. Run migrations first.")
            return
        with target_conn.cursor() as cur:
            quoted = ", ".join(f'"{t}"' for t in target_tables)
            cur.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE;")
        target_conn.commit()
        print("Target tables truncated.")
        print()

        total = 0
        for table in order:
            if table not in target_tables:
                continue
            source_cols = get_columns(source_conn, table)
            if not source_cols:
                continue
            target_cols = get_columns(target_conn, table)
            src_set, tgt_set = set(source_cols), set(target_cols)
            if src_set == tgt_set:
                cols = source_cols
            else:
                inter = src_set & tgt_set
                if "id" not in inter or not inter:
                    print(f"  SKIP {table}: column mismatch, no usable intersection (need id)")
                    continue
                # Use target order so INSERT matches target schema
                cols = [c for c in target_cols if c in inter]
                print(f"  {table}: using {len(cols)} shared columns (schema differs)")
            n = copy_table(source_conn, target_conn, table, cols, args.dry_run)
            total += n
            print(f"  {table}: {n} rows")
            if not args.dry_run:
                target_conn.commit()

        print()
        print(f"Total rows copied: {total}")

        if not args.dry_run and total > 0:
            print("Resetting sequences...")
            reset_sequences(target_conn, target_tables)
            target_conn.commit()
            print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        source_conn.rollback()
        target_conn.rollback()
        raise
    finally:
        source_conn.close()
        target_conn.close()


if __name__ == "__main__":
    main()
