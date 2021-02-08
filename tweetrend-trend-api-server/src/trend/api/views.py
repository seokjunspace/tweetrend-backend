from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..utils import *
from .exceptions import *
from .constants import *
import datetime
import jwt

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


def get_params(request):
    authenticate_request(request)
    try:
        from_time = int(request.query_params.get('from', None))  # time given in unix time
        to_time = request.query_params.get('to', None)
        if to_time is None:
            to_time = datetime.datetime.utcnow().timestamp()
        to_time = int(to_time)
        interval = interval_type[request.query_params.get('interval', None)]
        if interval == 'total':
            interval = to_time - from_time

        if from_time < 0 or to_time < 0:
            raise UnixTimeNeededError()
        if from_time > to_time:
            raise TimeReversed()
    except TypeError:
        raise TypeError("invalid time parameters received")
    except KeyError:
        raise KeyError("unsupported interval received")

    return from_time, to_time, interval


@api_view(['GET', ])
def api_get_total_count(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # start = time.time()
    data = get_total_count(topic, from_time, to_time, interval)
    # print("query time:", time.time()-start)
    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_user_count(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = get_user_count(topic, from_time, to_time, interval)

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_retweet_count(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = get_retweet_count(topic, from_time, to_time, interval)

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_region_counts(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = get_region_counts(topic, from_time, to_time, interval)

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_reputation(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = get_reputation(topic, from_time, to_time, interval)

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_source(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = get_source(topic, from_time, to_time, interval)

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_related_words(request, topic):
    try:
        from_time, to_time, interval = get_params(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    start = time.time()
    data = get_related_words(topic, from_time, to_time, interval)
    print("query time:", time.time()-start)

    return Response({"data": data}, status=status.HTTP_200_OK)
