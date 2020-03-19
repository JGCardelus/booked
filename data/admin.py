from django.contrib import admin

# Register your models here.
from .models import Teacher, Group, Meeting

admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(Meeting)
