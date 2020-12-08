import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Message

# python manage.py runserver

def index(request):
    return render(request, "network/index.html")

# Convert from compose in email project
@csrf_exempt
@login_required
def send_message(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    body = data.get("body", "")
    if body == [""]:
        return JsonResponse({
            "error": "Empty message."
        }, status=400)

    message = Message(
            sender=request.user,
            body=body)           
    message.save()

    return JsonResponse({"message": "Message posted."}, status=201)

@csrf_exempt
def load_messages(request, feed_type, sort_user, page):
    # Type of feed
    if feed_type == "posts":
        messages = Message.objects.all()
    elif feed_type == "following":

        data = User.objects.get(pk=sort_user).get_favorite()
        messages = Message.objects.filter(
            sender__in=data["favorite"]
        )
    elif feed_type == "profile":
        messages = Message.objects.filter(
            sender=sort_user
        )
    else:
        return JsonResponse({"error": "Invalid feed type."}, status=400)


    messages = messages.order_by("-timestamp").all()  
    messages = Paginator(messages, 10)

    message_data = {'Messages': [message.serialize(request.user) for message in messages.page(page)], 'Count': messages.count, 'Num': messages.num_pages} 
    return JsonResponse(message_data, safe=False)

@csrf_exempt
@login_required
def load_profile(request, user_id):
    try:
        profile = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    if request.method == "GET":
        return JsonResponse(profile.serialize(), safe=False)
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("status") is not None:
            requested_user_profile = User.objects.get(username=request.user)
            if str(request.user) == profile.username:
                pass
            elif data.get("status"): 
                profile.followers.add(request.user.id)
                requested_user_profile.favorite.add(profile.id)
            else: 
                profile.followers.remove(request.user.id)
                requested_user_profile.favorite.remove(profile.id)
        profile.save()
        requested_user_profile.save()
        return HttpResponse(status=204)            
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)  


@csrf_exempt
@login_required
def check_favorite(request, user_id):
    try:
        profile = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    if request.method == "GET":
        verify = str(request.user.id) == str(user_id)
        return JsonResponse(profile.check_status(request.user.id, verify), safe=False)     
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)  


@csrf_exempt
@login_required
def load_message_by_id(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found."}, status=404)

    # Return message contents
    if request.method == "GET":
        return JsonResponse(Message.serialize())

    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("liked") is not None:
            if data["liked"]:
                message.users_liked.add(request.user)
            else:
                message.users_liked.remove(request.user)
        elif data.get("edit_body") is not None:
            message.body = data["edit_body"]
        message.save()
        return HttpResponse(status=204)

    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
