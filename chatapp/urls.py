from django.urls import path
from chatapp import views

urlpatterns=[
    path('',views.Myview,name="index"),
    path('chatroom/<str:receiver>/',views.chatroom,name="chat_room"),
    path('signup/',views.signup,name='signup'),
    path('signin/',views.signin,name='signin'),
    path("logout/",views.logout_view,name='logout'),
    path("search/",views.search,name='search'),
    path('clearchat/<int:receiver_id>/',views.ClearChat,name='clearchat'),
    path('status/<int:receiver_id>/',views.StatusView,name='status'),
    path('unreadmessages/',views.Unread_messages,name='unreadmessage'),
    path('markasread/<int:receiver_id>/',views.Mark_as_read,name='markasread')
    # path('unread_msg/',views.unread_message,name='unread_msg')
]
