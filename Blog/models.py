from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, default=None)
    birthday = models.DateField(help_text='Required. Format: YYYY-MM-DD', default=timezone.now)
    user_country = models.CharField(max_length=30, default=None)
    user_city = models.CharField(max_length=30, default=None)
    user_email = models.EmailField(max_length=254, unique=True, default='noreply@gmail.com')


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('user_email', 'username', 'first_name', 'last_name', 'birthday', 'user_country', 'user_city')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
