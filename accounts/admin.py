from django.contrib import admin
from .models import Company, User, Project, Task, Membership

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "plan", "created_at")
    search_fields = ("name",)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "company", "role", "is_active")
    list_filter = ("role", "company")
    search_fields = ("username", "email")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "created_by", "created_at")
    list_filter = ("company",)
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "assigned_to", "created_at")
    list_filter = ("status", "project")
    search_fields = ("title",)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "joined_at")