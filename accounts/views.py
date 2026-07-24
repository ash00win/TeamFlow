from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UpgradePlanSerializer
from .permissions import IsOwner, IsManagerOrOwner, IsProjectMember
from .models import Project, Task, AuditLog, log_action
from .serializers import (
    CompanyRegisterSerializer,
    ProjectSerializer,
    TaskSerializer,
    AddUserSerializer,
    AuditLogSerializer,
)


from django.shortcuts import render

def signup_page(request):
    return render(request, "signup.html")

class RegisterCompanyView(APIView):
    serializer_class = CompanyRegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    @extend_schema(request=CompanyRegisterSerializer)
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Company created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=inline_serializer(
        name="ProtectedStatus",
        fields={
            "message": drf_serializers.CharField(),
            "user": drf_serializers.CharField(),
            "company": drf_serializers.CharField(allow_null=True),
            "role": drf_serializers.CharField(),
            "plan": drf_serializers.CharField(allow_null=True),
        },
    ))
    def get(self, request):
        return Response({
            "message": "You are authenticated!",
            "user": request.user.username,
            "company": request.user.company.name if request.user.company else None,
            "role": request.user.role,
            "plan": request.user.company.plan if request.user.company else None
        })


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(company=self.request.user.company)

    def get_permissions(self):

        if self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOwner]

        elif self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsManagerOrOwner]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):

        company = self.request.user.company

        if company.plan == "FREE":
            project_count = Project.objects.filter(company=company).count()

            if project_count >= 3:
                raise ValidationError(
                    {"error": "Free plan allows only 3 projects. Upgrade to PRO."}
                )

        project = serializer.save(
            company=company,
            created_by=self.request.user
        )

        log_action(company, self.request.user, "PROJECT_CREATED", project.name)

    def perform_destroy(self, instance):
        log_action(instance.company, self.request.user, "PROJECT_DELETED", instance.name)
        instance.delete()

class TaskViewSet(viewsets.ModelViewSet):

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        return Task.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):

        project = serializer.validated_data.get("project")

        if project.company != self.request.user.company:
            raise ValidationError("Project does not belong to your company")

        task = serializer.save(
            company=self.request.user.company
        )

        log_action(self.request.user.company, self.request.user, "TASK_CREATED", task.title)


class UpgradePlanView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UpgradePlanSerializer

    @extend_schema(request=UpgradePlanSerializer)
    def post(self, request):

        serializer = UpgradePlanSerializer(data=request.data)

        if serializer.is_valid():
            company = request.user.company
            new_plan = serializer.validated_data["plan"]

            company.plan = new_plan
            company.expiry_date = (
                timezone.now().date() + timedelta(days=30)
                if new_plan == "PRO"
                else None
            )
            company.save()

            log_action(company, request.user, "PLAN_UPGRADED", f"Plan changed to {new_plan}")

            return Response(
                {
                    "message": f"Company plan upgraded to {new_plan}"
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AddUserView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = AddUserSerializer

    @extend_schema(request=AddUserSerializer)
    def post(self, request):

        serializer = AddUserSerializer(
            data=request.data,
            context={"request":request}
        )

        if serializer.is_valid():

            new_user = serializer.save()

            log_action(
                request.user.company, request.user, "USER_ADDED",
                f"{new_user.username} added as {new_user.role}"
            )

            return Response(
                {"message":"User added successfully"},
                status=201
            )

        return Response(serializer.errors,status=400)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return AuditLog.objects.filter(company=self.request.user.company)