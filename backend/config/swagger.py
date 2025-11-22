from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# This will auto-discover ALL endpoints from all installed apps
schema_view = get_schema_view(
    openapi.Info(
        title="Support Plus API",
        default_version='v1',
        description="Unified API for benefits search, user management, and administration",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="Private License"),
    ),
    public=True,  # Set to True to allow unauthenticated access to docs
    permission_classes=(permissions.AllowAny,),
)