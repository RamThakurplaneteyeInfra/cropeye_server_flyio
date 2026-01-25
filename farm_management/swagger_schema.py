"""
Custom Swagger schema so all API modules (Users, Farms, Equipment, etc.) appear
as distinct tags in Swagger UI. Maps view __module__ to display tags.
"""
from drf_yasg.inspectors import SwaggerAutoSchema

# Map app module prefix -> Swagger tag (must match order of url includes)
APP_TAGS = {
    "users": "Users",
    "farms": "Farms",
    "equipment": "Equipment",
    "bookings": "Bookings",
    "inventory": "Inventory",
    "vendors": "Vendors",
    "messaging": "Messaging",
    "chatbot": "Chatbot",
    "tasks": "Tasks",
    "industries": "Industries",
}


class TaggedSwaggerAutoSchema(SwaggerAutoSchema):
    """Assigns a Swagger tag from the view's app module so all modules appear in UI."""

    def get_tags(self, operation_keys=None):
        view = self.view
        module = getattr(view, "__module__", "") or ""
        for prefix, tag in APP_TAGS.items():
            if prefix in module:
                return [tag]
        # Fallback: use first operation key (e.g. "users", "farms") as tag
        if operation_keys:
            name = operation_keys[0] if operation_keys else "api"
            return [name.replace("-", " ").title()]
        return super().get_tags(operation_keys)
