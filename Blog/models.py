from django.forms import ModelForm
from django.db import models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import os


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, default=None)
    birthday = models.DateField(help_text='Required. Format: YYYY-MM-DD', default=timezone.now)
    user_country = models.CharField(max_length=30, default=None)
    user_city = models.CharField(max_length=30, default=None)
    user_email = models.EmailField(max_length=254, unique=True, default='noreply@gmail.com')
    USERNAME_FIELD = 'username'


def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateField(default=timezone.now)
    title = models.CharField(max_length=50, default=None)
    content = models.CharField(max_length=10000, default=None)
    photo = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    url = models.SlugField(max_length=300)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    clicked = models.IntegerField(default=0)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateField(default=timezone.now)
    content = models.CharField(max_length=10000, default=None)


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('content', )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('user_email', 'username', 'first_name', 'last_name', 'birthday', 'user_country', 'user_city')


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('user_mail', 'password')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'photo')


class PostProfile(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def update_post(sender, instance, created, **kwargs):
    if created:
        PostProfile.objects.create(post=instance)
    instance.profile.save()
