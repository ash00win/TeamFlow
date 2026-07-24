from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import signup_page
from accounts.views import (
    RegisterCompanyView,
    ProtectedView,
    UpgradePlanView,
    ProjectViewSet,
    TaskViewSet,
    AddUserView,
    AuditLogViewSet,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [

    path('admin/', admin.site.urls),

    # Frontend pages
    path('', include('frontend.urls')),
    path('signup/', signup_page),
    # Auth APIs
    path('api/register/', RegisterCompanyView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/protected/', ProtectedView.as_view()),
    path('api/upgrade-plan/', UpgradePlanView.as_view()),
    path("api/add-user/", AddUserView.as_view()),
    # Project & Task APIs
    path('api/', include(router.urls)),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]