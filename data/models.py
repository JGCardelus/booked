from django.db import models

import datetime
import random

from django.utils import timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from booked.framework import parser, dt_filter

class User(models.Model):
    user_id = models.CharField(max_length=8, primary_key=True, unique=True)
    username = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=512)
    email = models.CharField(max_length=512)
    password = models.CharField(max_length=512)
    is_admin = models.BooleanField(default=False)

    def verify(in_username, in_password):
        user = None

        try:
            user = User.objects.get(username=in_username)
        except User.DoesNotExist:
            user = None

        if user == None:
            try:
                user = User.objects.get(email=in_username)
            except User.DoesNotExist:
                user = None

        if user == None:
            return False, None
        
        password = user.password
        if password == in_password:
            return True, user
        else:
            return False, None

    def new_user_checks(information):
        username = information["username"]
        email = information["email"]

        # Email and username must be unique
        is_repeated = True
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            is_repeated = False

        if not is_repeated:
            is_repeated = True
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                is_repeated = False

        if is_repeated:
            return False
        else:
            return True

    def new(information):
        verified_info = User.new_user_checks(information)
        if not verified_info:
            return False, None

        username = information["username"]
        name = information["name"]
        email = information["email"]
        password = information["password"]

        # Teacher parsing
        is_admin = False
        if information["is_admin"] == 'True':
            is_admin = True

        user_id = User.generate_userid(username, name)

        new_user = None
        try:
            new_user = User(user_id=user_id, username=username, 
                        name=name, email=email, password=password, 
                        is_admin=is_admin)
            new_user.save()
        except:
            return False, None
        

        session = Session.generate_session(new_user)
        return True, session

    def generate_userid(username, name):
        digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
        digest.update(bytes(username + name, 'utf-8'))
        bytes_hash_ = digest.finalize()
        hash_ = str(bytes_hash_.hex())

        user_id = None
        while True:
            index = random.randint(0, len(hash_) - 9)
            user_id = "".join(list(hash_)[index:(index + 8)])
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                break

        return user_id

class Group(models.Model):
    group_id = models.CharField(max_length=8, primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, blank=True)

class JoinedGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_groups(user):
        try:
            groups = JoinedGroup.objects.all().filter(user=user)
            return groups
        except Group.DoesNotExist:
            return None

class Meeting(models.Model):
    meeting_id = models.CharField(max_length=12, primary_key=True, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time = models.DateTimeField()
    duration = models.TimeField(default='01:00')
    description = models.CharField(max_length=1024, blank=True)
    links = models.CharField(max_length=2048, blank=True)

    def filter_by_group(group):
        meetings = []
        try:
            meetings = Meeting.objects.all().filter(group=group)
        except:
            return []
        return meetings

    def get_by_datetime(group, date, time):
        meetings = Meeting.filter_by_group(group)
        meetings = Meeting.apply_datetime_filters(meetings, date, time)
        return meetings

    def apply_datetime_filters(init_meetings, date, time):
        meetings = []
        for meeting in init_meetings:
            eval_date, eval_time = parser.parse_datetime_object(str(meeting.time))
            is_valid = dt_filter.apply(date, time, eval_date, eval_time)
            
            if is_valid:
                meetings.append(meeting)

        return meetings

    def get_by_range(group, date_a, time_a, date_b, time_b):
        meetings = Meeting.filter_by_group(group)
        meetings = Meeting.apply_range_filters(meetings, date_a, time_a, date_b, time_b)
        return meetings

    def apply_range_filters(init_meetings, date_a, time_a, date_b, time_b):
        meetings = []
        for meeting in init_meetings:
            eval_date, eval_time = parser.parse_datetime_object(str(meeting.time))
            is_valid = dt_filter.apply_range(date_a, time_a, date_b, time_b, eval_date, eval_time)

            if is_valid:
                meetings.append(meeting)

        return meetings


class Task(models.Model):
    task_id = models.CharField(max_length=12, primary_key=True, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    due_date = models.DateTimeField()
    notes = models.CharField(max_length=2048)

    def filter_by_group_name(group, name):
        tasks = []
        try:
            tasks = Task.objects.all().filter(group=group)
        except:
            return []

        if name != None:
            try:
                tasks = Task.objects.all().filter(name=name)
            except:
                return []

        return tasks

    def get_by_datetime(group, name, date, time):
        tasks = Task.filter_by_group_name(group, name)
        tasks = Task.apply_datetime_filters(tasks, date, time)
        return tasks

    def apply_datetime_filters(init_tasks, date, time):
        tasks = []
        for task in init_tasks:
            eval_date, eval_time = parser.parse_datetime_object(str(task.due_date))
            is_valid = dt_filter.apply(date, time, eval_date, eval_time)
            
            if is_valid:
                tasks.append(task)

        return tasks

    def get_by_range(group, name, date_a, time_a, date_b, time_b):
        tasks = Task.filter_by_group_name(group, name)
        tasks = Task.apply_range_filters(tasks, date_a, time_a, date_b, time_b)
        return tasks

    def apply_range_filters(init_tasks, date_a, time_a, date_b, time_b):
        tasks = []
        for task in init_tasks:
            eval_date, eval_time = parser.parse_datetime_object(str(task.due_date))
            is_valid = dt_filter.apply_range(date_a, time_a, date_b, time_b, eval_date, eval_time)
            if is_valid:
                tasks.append(task)

        return tasks

        

class Session(models.Model):
    session_key = models.CharField(max_length=256)
    expire_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def generate_session(user):
        date = timezone.now()
        user_id = user.user_id

        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(user_id + str(date) + user.email, 'utf-8'))
        session_key = digest.finalize()
        session_key = session_key.hex()

        expire_date = timezone.now() + datetime.timedelta(days=2)

        new_session = Session(session_key=session_key, expire_date=expire_date, user=user)
        new_session.save()

        return new_session

    def verify_session_key(session_key):
        try:
            session = Session.objects.get(session_key=session_key)
        except Session.DoesNotExist:
            return False, None
        else:
            return True, session

    def get_session(session_key):
        try:
            session = Session.objects.get(session_key=session_key)
        except Session.DoesNotExist:
            return None
        else:
            return session


