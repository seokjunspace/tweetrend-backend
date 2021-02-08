from mongoengine import *
import time
from collections import defaultdict
import json

with open("secrets.json", encoding='UTF-8') as f:
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



def get_total_count(topic, from_time, to_time, interval):
    # unix time으로 들어옴
    time = from_time
    data = list()
    while time < to_time:
        total_counts = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).sum(
            'total_counts')
        data.append({"date": time, "count": total_counts})
        time += interval

    return data


def get_user_count(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        user_counts = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).sum(
            'user_counts')
        data.append({"date": time, "count": user_counts})
        time += interval

    return data


def get_retweet_count(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        retweet_counts = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).sum(
            'retweet_counts')
        data.append({"date": time, "count": retweet_counts})
        time += interval

    return data


def get_region_counts(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        values = defaultdict(int)
        results = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).only(
            'region')
        for result in results:
            r = result.to_mongo().to_dict()["region"]
            for region, count in r.items():
                values[region] += count

        values = dict(sorted(values.items(), key=(lambda x: x[1]), reverse=True))
        region = list()
        for key, val in values.items():
            region.append({'name': key, 'counts': val})

        data.append({"date": time, "region": region})
        time += interval
    return data


def get_reputation(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        values = defaultdict(int)
        results = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).only(
            'reputation')
        for result in results:
            r = result.to_mongo().to_dict()["reputation"]
            for key, val in r.items():
                values[key] += val
        reputation = list()
        for key, val in values.items():
            reputation.append({'name': key, 'counts': val})

        data.append({"date": time, "reputation": reputation})
        time += interval
    return data


def get_source(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        values = defaultdict(int)
        results = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).only(
            'source')
        for result in results:
            r = result.to_mongo().to_dict()["source"]
            for source, cnt in r.items():
                values[source] += cnt

        values = dict(sorted(values.items(), key=(lambda x: x[1]), reverse=True))
        source = list()
        for key, val in values.items():
            source.append({'name': key, 'counts': val})

        data.append({"date": time, "source": source})
        time += interval
    return data


def get_related_words(topic, from_time, to_time, interval):
    time = from_time
    data = list()
    while time < to_time:
        words = defaultdict(int)
        scores = defaultdict(int)
        results = TimeTrendHour.objects(
            Q(topic=topic) & Q(collected_at__gte=time) & Q(collected_at__lt=time + interval)).only(
            'related_words')
        for result in results:
            r = result.to_mongo().to_dict()["related_words"]
            for word, val in r.items():
                words[word] += val[0]
                scores[word] = val[1]

        words = dict(sorted(words.items(), key=(lambda x: x[1]), reverse=True))
        relwords = list()
        for word in words:
            relwords.append({"name": word, "counts": words[word], "score": scores[word]})
            if len(relwords) >= 200:
                break
        data.append({"date": time, "relwords": relwords})
        time += interval
    return data
