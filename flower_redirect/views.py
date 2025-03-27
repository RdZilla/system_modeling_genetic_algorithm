from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin, login_url='/admin/login/')
def flower_redirect(request):
    return redirect("http://localhost:5555/flower")
