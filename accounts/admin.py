from django.contrib import admin
from .models import Company, User, Project, Task, Membership


admin.site.register(Company)
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Membership)