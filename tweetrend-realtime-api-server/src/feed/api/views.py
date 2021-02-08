from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import jwt
import datetime
import json
from .exceptions import *
from .utils import get_first_tweets, get_next_tweets

with open("secrets.json", encoding='UTF-8') as f:
    secrets = json.loads(f.read())


def authenticate_request(request):
    try:
        encoded_jwt = request.META['HTTP_AUTHORIZATION'].split(" ")[1]
        user_jwt = jwt.decode(encoded_jwt, secrets['secret_key'], algorithms=[secrets['algorithm']])
        if user_jwt['exp'] < datetime.datetime.utcnow().timestamp():
            raise ExpiredTokenError()

    except UnboundLocalError:
        raise InvalidTokenError()


@api_view(['GET', ])
def api_get_tweets(request, topic):
    """ retrieve 20 tweets of the requested topic """
    bottom_id = request.query_params.get('bottomId', None)

    if bottom_id is None:
        tweets = get_first_tweets(topic)
        if tweets:
            for tweet in tweets:
                tweet['data']['id'] = str(tweet['data']['id'])
            return Response({"tweets": tweets}, status=status.HTTP_200_OK)

        return Response({"error": "topic not supported"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        bottom_id = int(bottom_id)
        tweets = get_next_tweets(topic, bottom_id)
        if tweets:
            for tweet in tweets:
                tweet['data']['id'] = str(tweet['data']['id'])
            return Response({"tweets": tweets}, status=status.HTTP_200_OK)

        return Response({"error": "no tweets anymore"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def room(request, room_name):
    return render(request, 'feed/room.html', {
        'room_name': room_name
    })
