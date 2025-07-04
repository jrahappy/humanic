from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.index, name="index"),
    path("chat_window/<int:staff_id>/", views.chat_window, name="chat_window"),
    path("group/<int:group_id>/", views.group_chat_view, name="group_chat"),
    path("chat/<int:receiver_id>/", views.one_to_one_chat_view, name="one_to_one_chat"),
    path("send-message/", views.send_message, name="send_message"),
    path("create-group/", views.create_group, name="create_group"),
    path("join-group/<int:group_id>/", views.join_group, name="join_group"),
    path("presence/", views.check_presence, name="check_presence"),
    path("echo/", views.echo_page, name="echo_page"),
    # path('room/<str:room_name>/', views.room, name='room'),
    # path('chat/', views.chat, name='chat'),
]
