from django.test import TestCase


class FrontendPageTests(TestCase):
    """Smoke tests: each page renders successfully with its expected template."""

    def test_login_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_dashboard_page(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_projects_page(self):
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_tasks_page(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks.html")

    def test_upgrade_page(self):
        response = self.client.get("/upgrade/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upgrade.html")

    def test_team_page(self):
        response = self.client.get("/team/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "team.html")
