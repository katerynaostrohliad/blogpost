from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context, Template
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView, Response, status
from .models import User, SignUpForm, LoginForm, PostForm, Post, CommentForm, Like
from .serializers import UserSerializer
from Blog.tokens import account_activation_token
from rest_framework.decorators import api_view


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
                                 'http://{{ domain }}activate{{ uid }}{{ token }}.')
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
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get['username']
            password = request.POST.get['password']
            user = authenticate(request, username=username, password=password)
            login(request, user)
        if User.DoesNotExist:
            return render(request, 'login_failed.html')
        else:
            return redirect('home')

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


#@login_required
@api_view(['GET', 'POST'])
def home(request):
    if request.method == 'GET':
        return render(request, 'home_page.html', {'login': Login,
                                                  'signup': Signup,
                                                  'create': create,
                                                  })


#@login_required
@api_view(['GET', 'POST'])
def create(request):
    if request.method == 'POST':
        form = PostForm()
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        return Response('Posted!')
    else:
        form = PostForm()
        return render(request, 'post_creation.html', {"form": form})


@api_view(['GET', 'POST'])
def open_post(request):
    if request.method == 'POST':
        post = get_object_or_404(Post)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
        new_like = Like.objects.get_or_create(user=request.user, post=post)
        if not new_like:
            new_like.delete()
        else:
            new_like.save()
    else:
        post = get_object_or_404(Post)
        return render(request, 'post.html', {'post': post})


@api_view(['GET', 'POST'])
def posts(self, request):
    if request.method == 'POST':
        return redirect(open_post)
    else:
        post = Post.objects.all()
    return render(request, 'posts.html', {'posts': post})


#########
#def sorting(self, request):
    #pass

