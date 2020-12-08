from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("User", related_name="favorited")  
    favorite = models.ManyToManyField("User", related_name="followed")   
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": len(self.followers.all()),
            "favorite": len(self.favorite.all()),
        }
    def check_status(self, requested_user, verify):
        for user in self.followers.all():
            if user.id == requested_user:
                return {
                    "status": True,
                    "info": verify
                }
        return {
            "status": False,
            "info": verify
        }
    def get_favorite(self): 
        return {
            "favorite": self.favorite.all()
            } 


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_sent")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    users_liked = models.ManyToManyField(User, related_name="users_liked")

    def serialize(self, logged_user):
        return {
            "id": self.id,
            "username": self.sender.username,
            "user_id": self.sender.id,
            "body": self.body,
            "timestamp": self.timestamp.strftime('%b %d %Y, %I:%M %p'),
            "likes": len(self.users_liked.all()),
            "liked": logged_user in self.users_liked.all()
        }