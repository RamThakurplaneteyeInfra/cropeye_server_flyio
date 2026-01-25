"""
Fix phone number issues before Django migrations run
This script should be run before migrations to prevent unique constraint errors
Works without Django setup - uses direct database connection
"""
import os
import sys
import psycopg2

def fix_phone_before_migrations():
    """Fix phone number issues before migrations"""
    print("=" * 70)
    print("Fixing Phone Numbers Before Migrations")
    print("=" * 70)
    
    # Get database config from environment
    db_config = {
        'dbname': os.environ.get('DB_NAME', 'CROPDB_TEST'),
        'user': os.environ.get('DB_USER', 'farm_management_l1wj_user'),
        'password': os.environ.get('DB_PASSWORD', 'DySO3fcTFjb8Rgp9IZIxGYgLZ7KxwmjL'),
        'host': os.environ.get('DB_HOST', 'dev-et.cropeye.ai'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
            # Step 1: Check if column allows NULL
            cursor.execute("""
                SELECT is_nullable 
                FROM information_schema.columns
                WHERE table_name = 'users_user' 
                AND column_name = 'phone_number';
            """)
            result = cursor.fetchone()
            if result:
                is_nullable = result[0]
                if is_nullable == 'NO':
                    print("Making phone_number nullable...")
                    cursor.execute("""
                        ALTER TABLE users_user 
                        ALTER COLUMN phone_number DROP NOT NULL;
                    """)
                    print("OK: Column now allows NULL")
            
            # Step 2: Convert empty strings to NULL
            print("\nConverting empty strings to NULL...")
            cursor.execute("""
                UPDATE users_user
                SET phone_number = NULL
                WHERE phone_number = '' OR TRIM(phone_number) = '';
            """)
            updated = cursor.rowcount
            print(f"OK: Converted {updated} empty strings to NULL")
            
            # Step 3: Check for duplicates (non-NULL)
            cursor.execute("""
                SELECT phone_number, COUNT(*) 
                FROM users_user 
                WHERE phone_number IS NOT NULL AND phone_number != ''
                GROUP BY phone_number 
                HAVING COUNT(*) > 1;
            """)
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"\nWARNING: Found {len(duplicates)} duplicate phone numbers")
                print("This will be handled by Django migrations or needs manual fix")
            else:
                print("\nOK: No duplicate phone numbers found")
            
            # Step 4: Drop existing unique constraints/indexes if they exist
            print("\nDropping existing phone_number constraints/indexes...")
            
            # Drop unique constraint
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    DROP CONSTRAINT IF EXISTS users_user_phone_number_key;
                """)
                print("OK: Dropped users_user_phone_number_key")
            except Exception as e:
                print(f"Info: {e}")
            
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    DROP CONSTRAINT IF EXISTS users_user_phone_number_unique;
                """)
                print("OK: Dropped users_user_phone_number_unique")
            except Exception as e:
                print(f"Info: {e}")
            
            # Drop indexes
            cursor.execute("""
                DROP INDEX IF EXISTS users_user_phone_number_idx;
            """)
            cursor.execute("""
                DROP INDEX IF EXISTS users_user_phone_number_unique_idx;
            """)
            cursor.execute("""
                DROP INDEX IF EXISTS users_user_phone_number_aff54ffd_uniq;
            """)
            print("OK: Dropped existing indexes")
            
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("OK: Phone number issues fixed - ready for migrations")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    success = fix_phone_before_migrations()
    sys.exit(0 if success else 1)

