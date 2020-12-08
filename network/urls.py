
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("send_message", views.send_message, name="send_message"),
    path("messages/<str:feed_type>/<str:sort_user>/<int:page>", views.load_messages, name="messages"),
    path("message/<int:message_id>", views.load_message_by_id, name="message"),
    path("load_profile/<int:user_id>", views.load_profile, name="load_profile"),
    path("check_favorite/<int:user_id>", views.check_favorite, name="check_favorite"),
]
