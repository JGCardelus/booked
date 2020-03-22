from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template import Context
from data.models import Session, User

# Create your views here.
def dashboard(request, session_key):
    access, session = Session.verify_session_key(session_key)
    if access:
        is_admin = session.user.is_admin
        if is_admin:
            return render(request, 'dashboard/admin_dash.html')
        else:
            return render(request, 'dashboard/user_dash.html')
    else:
        return HttpResponse("Accessing incorrect page.")

def filters(request, session_key, params):
    access, session = Session.verify_session_key(session_key)
    if access:
        context = {"params": params}
        return render(request, 'dashboard/filters.html', context)

def groups(request, session_key):
    access, session = Session.verify_session_key(session_key)
    if access:
        return render(request, 'dashboard/groups.html')

def new_meeting(request, session_key, params):
    access, session = Session.verify_session_key(session_key)
    if access:
        is_admin = session.user.is_admin
        if is_admin:
            context = {"params": params}
            return render(request, 'dashboard/new_meeting.html')

def new_task(request, session_key, params):
    access, session = Session.verify_session_key(session_key)
    if access:
        is_admin = session.user.is_admin
        if is_admin:
            context = {"params": params}
            return render(request, 'dashboard/new_task.html')

