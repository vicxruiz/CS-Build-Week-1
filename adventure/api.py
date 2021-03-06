from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    player = request.user.player
    player_id = player.id
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)

@csrf_exempt
@api_view(["POST"])
def take_item(request):
    user = request.user
    player = user.player
    uuid = player.uuid
    room = player.room()
    item = request.data["item"]
    player_obj = model_to_dict(player)
    player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
    player_obj['username'] = user.username
    if item in player.inventory:
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "You've already got one of those!",
                "player": player_obj
            },
            safe=True,
        )
    if item in room.items:
        room.items.remove(item)
        room.save()
        player.inventory.append(item)
        player.save()
        player_obj = model_to_dict(player)
        player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
        player_obj['username'] = user.username
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "",
                "player": player_obj
            },
            safe=True,
        )
    return JsonResponse(
        {
            "uuid": uuid,
            "name": player.user.username,
            "title": room.title,
            "description": room.description,
            "inventory": player.inventory,
            "room_items": room.items,
            "message": "Something went wrong picking up that item",
            "player": player_obj
        },
        safe=True,
    )


@csrf_exempt
@api_view(["POST"])
def drop_item(request):
    user = request.user
    player = user.player
    uuid = player.uuid
    room = player.room()
    item = request.data["item"]
    player_obj = model_to_dict(player)
    player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
    player_obj['username'] = user.username
    if item in player.inventory:
        player.inventory.remove(item)
        player.save()
        room.items.append(item)
        room.save()
        player_obj = model_to_dict(player)
        player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
        player_obj['username'] = user.username
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "",
                "player": player_obj
            },
            safe=True,
        )
    else:
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "Something went wrong dropping that item",
                "player": player_obj
            },
            safe=True,
        )

@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
