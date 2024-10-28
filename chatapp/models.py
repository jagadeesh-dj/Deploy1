from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    profile=models.ImageField(upload_to='profile',null=True)
    bio=models.TextField(null=True)
    last_login=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name="sender")
    receiver=models.ForeignKey(User,on_delete=models.CASCADE,related_name="receiver")
    message=models.TextField(null=True)
    data=models.FileField(null=True)
    description=models.TextField(null=True)
    clear_by_sender=models.BooleanField(default=False)
    clear_by_receiver=models.BooleanField(default=False)
    is_read=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.receiver}'
    


class UserStatus(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_status')
    status=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)
    