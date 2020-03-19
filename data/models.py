from django.db import models

class Teacher(models.Model):
    teacher_id = models.CharField(max_length=8, primary_key=True)
    username = models.CharField(max_length=128)
    name = models.CharField(max_length=512)
    email = models.CharField(max_length=512)
    password = models.CharField(max_length=512)

class Group(models.Model):
    group_id = models.CharField(max_length=8, primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)

class Meeting(models.Model):
    meeting_id = models.CharField(max_length=12, primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time = models.DateTimeField()
    repeat = models.CharField(max_length=512)
    description = models.CharField(max_length=1024)
    links = models.CharField(max_length=2048)