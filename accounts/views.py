from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .serializers import UpgradePlanSerializer
from .permissions import IsOwner, IsManagerOrOwner, IsProjectMember
from .models import Project, Task
from .serializers import (
    CompanyRegisterSerializer,
    ProjectSerializer,
    TaskSerializer
)



class RegisterCompanyView(APIView):
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Company created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

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

        serializer.save(
            company=company,
            created_by=self.request.user
        )


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        return Task.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")

        if project.company != self.request.user.company:
            raise PermissionError("Cannot add task to another company project")

        serializer.save(company=self.request.user.company)
        
        
class UpgradePlanView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):

        serializer = UpgradePlanSerializer(data=request.data)

        if serializer.is_valid():
            company = request.user.company
            new_plan = serializer.validated_data["plan"]

            company.plan = new_plan
            company.save()

            return Response(
                {
                    "message": f"Company plan upgraded to {new_plan}"
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)