from mongoengine import *
import time
from collections import defaultdict
import json
import asyncio
import constant

with open("../secrets.json", encoding='UTF-8') as f:
    secrets = json.loads(f.read())

connect('trend', username=secrets['username'], password=secrets['password'],
        authentication_source=secrets['authentication_source'], host=secrets['host'],
        port=secrets['port'])


class Region(DynamicEmbeddedDocument):
    pass


class Keyword(DynamicEmbeddedDocument):
    pass


class Reputation(EmbeddedDocument):
    positive = IntField()
    negative = IntField()
    neutral = IntField()


class Source(DynamicEmbeddedDocument):
    pass


class TimeTrendHour(Document):
    topic = StringField(required=True)
    collected_at = IntField(required=True)
    total_counts = IntField(required=True)
    user_counts = IntField(required=True)
    retweet_counts = IntField(required=True)
    region = EmbeddedDocumentField(Region)
    related_words = EmbeddedDocumentField(Keyword)
    reputation = EmbeddedDocumentField(Reputation)
    source = EmbeddedDocumentField(Source)
    meta = {
        'index': [
            ('topic', '-collected_at')
        ]
    }


class TimeTrendKor(DynamicDocument):
    pass


def _summarize_values(maindict, subdict):
    for key, val in subdict.items():
        maindict[key] += val
    return maindict


async def summarize(start_time, topic):
    print(topic, start_time)
    interval = constant.BATCH_TIME
    subsets = TimeTrendKor.objects(
        Q(topic=topic)
        & Q(collected_at__gte=start_time)
        & Q(collected_at__lt=start_time + interval))

    total_counts = subsets.sum('total_counts')
    user_counts = subsets.sum('user_counts')
    retweet_counts = subsets.sum('retweet_counts')

    reputation = defaultdict(int)
    region = defaultdict(int)
    source = defaultdict(int)
    related_words = defaultdict(int)
    related_words_reputation = dict()
    result_words = dict()

    for subset in subsets:
        sub = subset.to_mongo().to_dict()  # 하나의 1분짜리 도큐멘트
        region = _summarize_values(region, sub['region'])
        reputation = _summarize_values(reputation, sub['reputation'])
        source = _summarize_values(source, sub['source'])
        for key, val in sub['related_words'].items():
            related_words[key] += val[0]
            related_words_reputation[key] = val[1]

    for word, cnt in related_words.items():
        result_words[word] = (cnt, related_words_reputation[word])

    region = dict(sorted(region.items(), key=(lambda x: x[1]), reverse=True))
    source = dict(sorted(source.items(), key=(lambda x: x[1]), reverse=True))
    result_words = dict(sorted(result_words.items(), key=(lambda x: x[1]), reverse=True)[0:20])
    TimeTrendHour(topic=topic, collected_at=start_time,
                  total_counts=total_counts,
                  user_counts=user_counts,
                  retweet_counts=retweet_counts,
                  region=region,
                  related_words=result_words,
                  reputation=reputation,
                  source=source).save()


async def main(target_time):
    await asyncio.gather(summarize(target_time, constant.TOPIC_LIST[0]))


target_time = constant.START_TIME

while True:
    asyncio.run(main(target_time))
    time.sleep(constant.BATCH_TIME)
    target_time += constant.BATCH_TIME