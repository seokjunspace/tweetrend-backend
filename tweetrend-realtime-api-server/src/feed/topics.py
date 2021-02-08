import json
import threading
import asyncio

from channels.layers import get_channel_layer
from .utils import get_realtime_tweet


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        try:
            await asyncio.sleep(self._timeout)
            await self._callback()
        except Exception as ex:
            print(ex)

    def cancel(self):
        self._task.cancel()


class Topic:
    def __init__(self, topic, top_id):
        self.name = topic
        self.top_id = top_id
        self.count = 1

    def __del__(self):  # 성공적으로 객체가 제거되는지 확인하기 위한 테스트용 함수
        print(self.name, "가비지컬렉터에 의한 소멸 확인")

    def add_count(self):
        self.count += 1

    def subtract_count(self):
        self.count -= 1

    def is_not_inquired_anymore(self):
        if self.count == 0:
            return True
        return False

    def __str__(self):
        return self.name


class TopicStorage:
    storage = list()  # 현재 클라이언트의 요청에 의해 조회되고 있는 토픽의 목록

    def add_topic(topic):
        """ 새로운 토픽을 저장소에 추가하고 해당 토픽의 실시간 함수 가동시킴 """
        TopicStorage.storage.append(topic)
        RealtimeSender(topic)

    def discard_topic(topic):
        """ 더이상 해당 토픽에 대한 요청을 하는 클라이언트가 없으면 저장소에서 제거 """
        print(topic, "저장소에서 제거되는 것 확인")
        TopicStorage.storage.remove(topic)

    def retrieve_topic_by_name(topic_name):
        index = TopicStorage.has_topics_by_name().index(topic_name)
        return TopicStorage.storage[index]

    def contains_topic(topic):
        """ 해당 토픽 인스턴스가 존재하는지 비교 """
        if topic in TopicStorage.storage:
            return True
        return False

    def contains_topic_by_name(topic_name):
        """ 해당 토픽 인스턴스 존재 여부를 이름으로 비교 """
        if topic_name in TopicStorage.has_topics_by_name():
            return True
        return False

    @classmethod
    def has_topics_by_name(cls):
        """ 이름으로 토픽의 존재 여부를 판별하기 위한 함수, 추후 삭제및 개선 요망"""
        topic_list = []
        for topic in TopicStorage.storage:
            topic_list.append(topic.name)
        return topic_list


class RealtimeSender:
    def __init__(self, topic_instance):
        self.topic = topic_instance
        # self.keep_sending_tweets()  # 실시간 함수 발동
        self.timer = Timer(0, self.keep_sending_tweets)

    async def keep_sending_tweets(self):
        channel_layer = get_channel_layer()

        if TopicStorage.contains_topic(self.topic):
            serialized_tweets = await get_realtime_tweet(self.topic.name, self.topic.top_id)
            """ 조회된 트윗이 있는 경우에만 제공 """
            if serialized_tweets:
                self.topic.top_id = serialized_tweets[0]['data']['id']
                await channel_layer.group_send(
                    self.topic.name, {
                        "type": "send.tweets",
                        "tweets": json.dumps(serialized_tweets),
                    }
                )
            else:
                print(self.topic.name, "에 대해 새로 생성된 트윗이 없다")

            self.timer = Timer(3, self.keep_sending_tweets)

        else:
            self.timer.cancel()
            print("토픽 삭제가 성공적으로 반영되었고 실시간 함수는 중단될 것이다.")
