import json
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
# from django.contrib.auth.models import User
from .models import Message,UserStatus,User
from django.utils.timezone import now
import os
import base64
from django.conf import settings

class Mainsocket(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name="funchat"
        print(self.group_name)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self,text_data):
        data=json.loads(text_data)
        types=data.get('type','')
        users=data.get('user','')
        status=data.get('status','')

        if types=='user':
            await self.save_user_status(users,status)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'funchat_user',
                    'user': users,
                    'status': status
                }
            )
    async def funchat_user(self,event):
        users=event['user']
        status=event['status']

        await self.send(text_data=json.dumps({
            'type':'user_status',
            'status':status,
            'user': users
            })
        )
    @sync_to_async
    def save_user_status(self,users,status):
        myuser=User.objects.get(id=users)
        model=UserStatus.objects.filter(user=myuser).exists()
        if model:
            UserStatus.objects.filter(user=myuser).update(status=status,timestamp=now())
        else:
            UserStatus.objects.create(user=myuser,status=status,timestamp=now())


class chatconsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender=self.scope['user'].id
        self.receiver=self.scope['url_route']['kwargs']['receiver']

        if int(self.sender) > int(self.receiver):
            self.room_name=f'{self.sender}--{self.receiver}'
        else:
            self.room_name=f'{self.receiver}--{self.sender}'

        self.group_room_name='chat_%s' % self.room_name

        print(self.group_room_name)
        await self.channel_layer.group_add(
            self.group_room_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_room_name,
            self.channel_name
        )
    
        
    async def receive(self,text_data):
        data=json.loads(text_data)
        # print(data['type'])
        types=data.get('type','')
        typing_indicator=data.get('bool','')
        file=data.get('file','')
        filedata=data.get('filedata','')
        type_icon_receiver=data.get('typing_icon_receiver','')
        message=data.get('message','')
        sender=data.get('sender','')
        receiver=data.get('receiver','')
        status=data.get('status','')
        print(types)

        if types=="message":
            await self.save_message(sender,receiver,message)
            await self.channel_layer.group_send(
                self.group_room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )
        elif types=='File':
            filedata=filedata.split(",")[1]
            await self.Save_files(sender,receiver,file)
            decoded_file = base64.b64decode(filedata)
            file_path = os.path.join(settings.MEDIA_ROOT, file)

            with open(file_path, "wb") as f:
                f.write(decoded_file)

            await self.channel_layer.group_send(
                self.group_room_name,
                {
                    'type': 'chat_file',
                    'file': file,
                    'sender': sender
                }
            )

        elif types=='typing':
            await self.channel_layer.group_send(
                self.group_room_name,
                {
                    'type': 'chat_typing',
                    'typing_indicator': typing_indicator,
                    'type_icon_receiver':type_icon_receiver
                }
            )
        elif types=='online_status':
            await self.channel_layer.group_send(
                self.group_room_name,
                {
                    'type':'chat_status',
                    'sender':sender,
                    'status':status
                }
            )

    async def chat_typing(self,event):
        typing_indicator=event['typing_indicator']
        type_icon_receiver=event['type_icon_receiver']

        await self.send(text_data=json.dumps({
            'type':'typing',
            'bool':typing_indicator,
            'type_icon_receiver': type_icon_receiver
        }))

    async def chat_message(self,event):
        message=event['message']
        sender=event['sender']

        await self.send(text_data=json.dumps({
            'type':'message',
            'message':message,
            'sender':sender,
        }))

    async def chat_file(self,event):
        file=event['file']
        sender=event['sender']

        await self.send(text_data=json.dumps({
            'type':'files',
            'file': file,
            'sender':sender
        }))

    async def chat_status(self,event):
        user=event['sender']
        status=event['status']

        await self.send(text_data=json.dumps({
            'type':'status',
            'user':user,
            'status':status
        }))

    @sync_to_async
    def save_message(self,sender,receiver,message):
        sender=User.objects.get(id=sender)
        receiver=User.objects.get(id=receiver)

        Message.objects.create(sender=sender,receiver=receiver,message=message)

    @sync_to_async
    def Save_files(self,sender,receiver,file):
        sender=User.objects.get(id=sender)
        receiver=User.objects.get(id=receiver)

        Message.objects.create(sender=sender,receiver=receiver,data=file)