from django.db import models

import datetime
import random

from base64 import b64encode
from django.utils import timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

class User(models.Model):
    user_id = models.CharField(max_length=8, primary_key=True, unique=True)
    username = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=512)
    email = models.CharField(max_length=512)
    password = models.CharField(max_length=512)
    is_teacher = models.BooleanField(default=False)

    def verify(in_username, in_password):
        user = None
        try:
            # Also email
            user = User.objects.get(username=in_username)
        except User.DoesNotExist:
            return False, None
        else:
            password = user.password
            if password == in_password:
                return True, user
            else:
                return False, None

    def new_user_checks(information):
        username = information["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return True
        else:
            return False

    def new(information):
        verified_info = User.new_user_checks(information)
        if not verified_info:
            return False, None

        username = information["username"]
        name = information["name"]
        email = information["email"]
        password = information["password"]

        # Teacher parsing
        is_teacher = False
        if information["is_teacher"] == 'True':
            is_teacher = True

        user_id = User.generate_userid(username, name)

        new_user = None
        try:
            new_user = User(user_id=user_id, username=username, 
                        name=name, email=email, password=password, 
                        is_teacher=is_teacher)
            new_user.save()
        except:
            return False, None
        

        session = Session.generate_session_key(new_user)
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
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)

class Meeting(models.Model):
    meeting_id = models.CharField(max_length=12, primary_key=True, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time = models.DateTimeField()
    repeat = models.CharField(max_length=512)
    description = models.CharField(max_length=1024)
    links = models.CharField(max_length=2048)

class Session(models.Model):
    session_key = models.CharField(max_length=256)
    expire_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def generate_session_key(user):
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


