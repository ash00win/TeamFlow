from rest_framework.test import APITestCase
from rest_framework import status

from .models import Company, User, Project, Task


class TenantIsolationTests(APITestCase):
    """Company A must never be able to see or touch Company B's data."""

    def setUp(self):
        self.company_a = Company.objects.create(name="Company A", plan="FREE")
        self.company_b = Company.objects.create(name="Company B", plan="FREE")

        self.owner_a = User.objects.create_user(
            username="owner_a", password="pass12345",
            company=self.company_a, role="OWNER",
        )
        self.owner_b = User.objects.create_user(
            username="owner_b", password="pass12345",
            company=self.company_b, role="OWNER",
        )

        self.project_b = Project.objects.create(
            company=self.company_b, name="Company B Project", created_by=self.owner_b,
        )
        self.task_b = Task.objects.create(
            company=self.company_b, project=self.project_b, title="Company B Task",
        )

    def test_project_list_excludes_other_company(self):
        self.client.force_authenticate(user=self.owner_a)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p["id"] for p in response.data]
        self.assertNotIn(self.project_b.id, ids)

    def test_task_list_excludes_other_company(self):
        self.client.force_authenticate(user=self.owner_a)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [t["id"] for t in response.data]
        self.assertNotIn(self.task_b.id, ids)

    def test_cannot_fetch_other_companys_project_by_id(self):
        self.client.force_authenticate(user=self.owner_a)
        response = self.client.get(f"/api/projects/{self.project_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_task_under_other_companys_project(self):
        self.client.force_authenticate(user=self.owner_a)
        response = self.client.post("/api/tasks/", {
            "title": "Sneaky task",
            "project": self.project_b.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FreePlanLimitTests(APITestCase):
    """Free plan companies are capped at 3 projects."""

    def setUp(self):
        self.company = Company.objects.create(name="Free Co", plan="FREE")
        self.owner = User.objects.create_user(
            username="owner", password="pass12345",
            company=self.company, role="OWNER",
        )
        self.client.force_authenticate(user=self.owner)

    def test_can_create_up_to_three_projects(self):
        for i in range(3):
            response = self.client.post("/api/projects/", {"name": f"Project {i}"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fourth_project_is_blocked_on_free_plan(self):
        for i in range(3):
            self.client.post("/api/projects/", {"name": f"Project {i}"})

        response = self.client.post("/api/projects/", {"name": "Project 4"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.filter(company=self.company).count(), 3)

    def test_fourth_project_allowed_on_pro_plan(self):
        self.company.plan = "PRO"
        self.company.save()

        for i in range(4):
            response = self.client.post("/api/projects/", {"name": f"Project {i}"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RolePermissionTests(APITestCase):
    """Members can't do Owner/Manager-only things like create projects or add users."""

    def setUp(self):
        self.company = Company.objects.create(name="RBAC Co", plan="PRO")
        self.owner = User.objects.create_user(
            username="rbac_owner", password="pass12345",
            company=self.company, role="OWNER",
        )
        self.manager = User.objects.create_user(
            username="rbac_manager", password="pass12345",
            company=self.company, role="MANAGER",
        )
        self.member = User.objects.create_user(
            username="rbac_member", password="pass12345",
            company=self.company, role="MEMBER",
        )
        self.project = Project.objects.create(
            company=self.company, name="Shared Project", created_by=self.owner,
        )

    def test_member_cannot_create_project(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post("/api/projects/", {"name": "Member Project"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_project(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post("/api/projects/", {"name": "Manager Project"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_cannot_delete_project(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_project(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_cannot_add_user(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post("/api/add-user/", {
            "username": "newbie", "email": "newbie@example.com",
            "password": "pass12345", "role": "MEMBER",
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_add_user(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post("/api/add-user/", {
            "username": "newbie", "email": "newbie@example.com",
            "password": "pass12345", "role": "MEMBER",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
