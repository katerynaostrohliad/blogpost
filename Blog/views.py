from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, render_to_response
from django.template import Context, Template
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView, Response, status
from .models import User, SignUpForm, LoginForm
from .serializers import UserSerializer
from Blog.tokens import account_activation_token


class Signup(APIView):

    def post(self, request):
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user_email = form.cleaned_data.get('user_email')
                user = authenticate(username=username, password=raw_password)
                current_site = get_current_site(request)
                subject = 'Activate Your Blog Account'

                t = Template('Hi {{ user }}! '
                                 'To activate your account, please, go to the following link '
                                 'http://{{ domain }}activate{{uid}}{{token}}.')
                message = Context({
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                content = t.render(message)
                from_email = 'noreply@gmail.com'
                msg = EmailMultiAlternatives(subject, content, from_email, user_email)
                msg.send()
                return redirect('Activationsent')
            else:
                form = SignUpForm()
                return render_to_response(request, 'my_signup_form.html', {"form": form})
        return Response(status=200)

    def get(self, request):
        form = SignUpForm()
        return render(request, 'my_signup_form.html', {"form": form})


class Activationsent(APIView):

    def get(self, request):
        return Response('Account activation sent.')


def activate(self, request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_serializer = UserSerializer(user, many=True)
        user = user_serializer.data
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return Response('Logged in')
    else:
        t = Template('{{ user }} your login failed. Please, check if you have activated your email.')
        message = Context({
            'user': user,
        })
        content = t.render(message)
        return render(request, content)


class Login(APIView):

    def post(self, request):
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                try:
                    user_email = request.POST.get['user_email']
                    password = request.POST.get['password']
                    user = authenticate(request, user_email=user_email, password=password)
                    login(request, user)
                    return redirect(home)
                except User.DoesNotExist:
                    return Response('Password or email is wrong.')

    def get(self, request):
        form = LoginForm()
        return render(request, 'login_form.html', {'form': form})


class Logout(APIView):

    def get(self, request):
        logout(request)
        return Response('You have successfully logged out.')


class Getinfo(APIView):

    @login_required
    def get(self, request):
        info = User.objects.all()
        user_serializer = UserSerializer(info, many=True)
        info = user_serializer.data
        return Response(info, status=status.HTTP_200_OK)


@login_required
def home(request):
    return Response('Home Page')
