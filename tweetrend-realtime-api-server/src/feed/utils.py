from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from .api.serializers import TweetsSerializer
import datetime
import json

with open("secrets.json", encoding='UTF-8') as f:
    secrets = json.loads(f.read())


async def get_realtime_tweet(topic, top_id):
    lbp = DCAwareRoundRobinPolicy(local_dc='datacenter1')
    cluster = Cluster(secrets["cluster_ip"], protocol_version=4, load_balancing_policy=lbp)
    connection = cluster.connect()
    connection.execute('use tweettrend')

    created_at = datetime.datetime.utcnow()
    query_time = created_at.strftime("%Y-%m-%dT%H:%M:%S").split('T')
    datehour = int(''.join(query_time[0].split('-')[1:]) + ''.join(query_time[1].split(':')[:2]))

    value = {'topic': topic, 'top_id': top_id,
             'datehour1': datehour + 1, 'datehour': datehour, 'datehour2': datehour - 1,
             'created_at1': created_at - datetime.timedelta(minutes=1),
             'created_at2': created_at + datetime.timedelta(minutes=1)}
    sql = "select * from tweets where topic=%(topic)s and datehour in (%(datehour1)s, %(datehour)s ,%(datehour2)s) " \
          "and created_at>=%(created_at1)s and created_at <=%(created_at2)s;"
    tweets = connection.execute(sql, value)

    serializer = TweetsSerializer(instance=tweets, many=True)
    converted_tweets = []
    for tweet in serializer.data:
        data = {}
        for key, value in tweet.items():
            if key != 'includes':
                data[key] = value
        converted_tweets.append({'data': data, 'includes': tweet['includes']})

    return converted_tweets
