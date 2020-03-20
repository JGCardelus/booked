from django.http import HttpResponse, Http404
from django.shortcuts import render

from data.models import Session, User

# Create your views here.
def dashboard(request, session_key):
    access, session = Session.verify_session_key(session_key)
    if access:
        is_teacher = session.user.is_teacher
        if is_teacher:
            return render(request, 'dashboard/admin_dash.html')
        else:
            return render(request, 'dashboard/user_dash.html')
    else:
        return HttpResponse("Accessing incorrect page.")