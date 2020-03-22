from django.contrib import admin

# Register your models here.
from .models import User, Group, Meeting, Session, Task, JoinedGroup

admin.site.register(User)
admin.site.register(Group)
admin.site.register(JoinedGroup)
admin.site.register(Meeting)
admin.site.register(Task)
admin.site.register(Session)
