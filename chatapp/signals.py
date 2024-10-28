from django.contrib.auth.signals import user_logged_in,user_logged_out
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import UserStatus,Message,User
from django.utils.timezone import now
from django.db.models.signals import pre_save,post_save
from django.core.cache import cache

# @receiver(user_logged_in)
# def Update_User_Online(sender,request,user,**kwargs):
#     model=UserStatus.objects.filter(user=user).exists()
#     if model:
#         UserStatus.objects.filter(user=user).update(status=True,timestamp=now())
#     else:
#         UserStatus.objects.create(user=user,status=True,timestamp=now())


@receiver(user_logged_out)
def Update_User_offline(sender,request,user,**kwargs):
    UserStatus.objects.filter(user=user).update(status=False,timestamp=now())

# @receiver(pre_save,sender=Message)
# def Mark_as_read(sender,instance,**kwargs):
#     mychannels=get_channel_layer()
#     print(instance.receiver.username)
#     channel_name = cache.get(f"user_{instance.sender.id}_channel")
#     print(channel_name)