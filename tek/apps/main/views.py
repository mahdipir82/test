from django.shortcuts import render
from django.conf import settings
def media_admin(request):
    return {"media_url" : settings.MEDIA_URL,}



from apps.accounts.forms import LoginUserForm, RegisterUserForm,VerifyRegisterForm,ChangePasswordForm,RememberPasswordForm
from django.shortcuts import render

def index(request):
    login_form = LoginUserForm()
    register_form = RegisterUserForm()
    verify_form = VerifyRegisterForm()
    changepassword_form = ChangePasswordForm()
    rememberpassword_form = RememberPasswordForm()
    return render(request, 'main/index.html', {
        "login_form": login_form,
        "register_form": register_form,
        "verify_form": verify_form,
        "changepassword_form": changepassword_form,
        "rememberpassword_form": rememberpassword_form,
    })