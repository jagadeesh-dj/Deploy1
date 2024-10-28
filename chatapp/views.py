from django.shortcuts import render,redirect,get_object_or_404
from .models import Message,UserStatus,User
from django.http import JsonResponse
# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Count


@login_required
def ClearChat(request,receiver_id):
    user=request.user
    receiver=get_object_or_404(User,id=receiver_id)

    Message.objects.filter(sender=user,receiver=receiver).update(clear_by_sender=True)
    Message.objects.filter(sender=receiver,receiver=user).update(clear_by_receiver=True)

    return JsonResponse({'status':'successfully Cleared'})

@login_required(login_url='/signin/')
def Myview(request):
    if not request.user.is_authenticated:
        return render(request,'signin.html')
    else:
        users=User.objects.exclude(username=request.user)
        current_user=request.user

        # sender=Message.objects.filter(sender=request.user).values_list('receiver',flat=True)
        # receiver = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
        # chatted_users_ids = set(sender).union(set(receiver))
        # chatted_users = User.objects.filter(id__in=chatted_users_ids)
        # read=Message.objects.filter(is_read=False)
        
        # print([i.id for i in read])
        return render(request,'index.html',{"users": users,'current_user':current_user})

@login_required
def search(request):
    users=User.objects.exclude(username=request.user)
    data=[{'username':i.username,'id':i.id} for i in users]
    return JsonResponse(data=data,safe=False)

@login_required(login_url='/signin/')
def chatroom(request,receiver):
    users=User.objects.exclude(username=request.user)
    receiver=User.objects.get(id=receiver)
    sender=request.user
    # message=Message.objects.filter(sender=sender,receiver=receiver,clear_by_sender=False)|Message.objects.filter(sender=receiver,receiver=sender,clear_by_receiver=False).order_by('timestamp')
    # unread_msg=Message.objects.filter(receiver=request.user,is_read=False)
    # for unread in unread_msg:
    #     unread.is_read=True
    #     unread.save()
    message = Message.objects.filter(
        (Q(sender=sender, receiver=receiver, clear_by_sender=False) | 
         Q(sender=receiver, receiver=sender, clear_by_receiver=False))
    ).order_by('timestamp')


    
    data={'message':list(message.values()),
           'sender':request.user.id,
           'receiver_id':receiver.id,
           'receiver_name':receiver.username,
           'sender_name':request.user.username,
           }
           
    return JsonResponse(data,safe=False)
    # return render(request,'chatroom.html',{"message": message,"sender": sender,"receiver": receiver,'users':users})

# def unread_message(request):
#     receiver=request.user.id
#     unread_msg=Message.objects.filter(receiver=receiver,is_read=False)
#     unread_msglist=[
#         {
#             'sender':unread.sender.username,
#             'receiver':unread.receiver.username,
#             'message':unread.message,
#             'is_read':unread_msg.count(),
#         }
#         for unread in unread_msg
#     ]
#     return JsonResponse(unread_msglist,safe=False)


def signup(request):
    if request.method=='POST':
        username=request.POST.get("username")
        mail=request.POST.get("mail")
        password=request.POST.get("password")
        confirm_pass=request.POST.get("confirm_pass")
        if username=="" or mail=="" or password=="" or confirm_pass=="":
            messages.warning(request,'Empty Values not accepted')
            return redirect('/signup')
        else:
            if User.objects.filter(username=username).exists():
                messages.warning(request,f'Username already taken')
                return redirect('/signup')
            if User.objects.filter(email=mail).exists() or mail.endswith('@gmail.com')==False:
                messages.warning(request,f'Mail already exists or invalid mail')
                return redirect('/signup')
            if password==confirm_pass:
                model=User.objects.create_user(username=username,email=mail,password=password)
                model.save()
                messages.success(request,'Account created sccessfully')
                return redirect('signin')
            else:
                messages.warning(request,'Confirm password not match!')
                return redirect('/signup')    
    return render(request,'signup.html')

def signin(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username=="" or password=="":
            messages.warning(request,'Empty values not accepted')
            return redirect('/signin')
        else:
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('index')
            else:
                messages.warning(request,"Username or Password Incorrect")
                return redirect('signin')
    return render(request,'signin.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request,'successfully logout')
    return redirect('signin')

@login_required
def StatusView(request,receiver_id):
    user=User.objects.get(id=receiver_id)
    status=UserStatus.objects.filter(user=user)
    return JsonResponse(data=list(status.values()),safe=False)


@login_required
def Mark_as_read(request,receiver_id):
    if request.method=='POST':
        receiverid=User.objects.get(id=receiver_id)
        Message.objects.filter(receiver=receiverid).update(is_read=True)
        return JsonResponse({'status':'success'})
    return JsonResponse({'status':'unable to complete task'})

@login_required
def Unread_messages(request):
    unread_data=Message.objects.filter(is_read=False)
    return JsonResponse(data=list(unread_data.values()),safe=False)

