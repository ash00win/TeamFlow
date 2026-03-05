from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import (
    RegisterCompanyView,
    ProtectedView,
    UpgradePlanView,
    ProjectViewSet,
    TaskViewSet
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [

    path('admin/', admin.site.urls),

    # Frontend pages
    path('', include('frontend.urls')),

    # Auth APIs
    path('api/register/', RegisterCompanyView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/protected/', ProtectedView.as_view()),
    path('api/upgrade-plan/', UpgradePlanView.as_view()),

    # Project & Task APIs
    path('api/', include(router.urls)),
]