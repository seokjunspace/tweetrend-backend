import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .topics import Topic, TopicStorage


class FeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.topic_name = self.scope['url_route']['kwargs']['topic']

        await self.channel_layer.group_add(
            self.topic_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        try:
            current_topic = TopicStorage.retrieve_topic_by_name(self.topic_name)
            current_topic.subtract_count()
            if current_topic.is_not_inquired_anymore():
                TopicStorage.discard_topic(current_topic)
                print("토픽스토리지에서 제거 후 토픽 제거되어 소멸자 발동되는지 확인할것")
        except:
            print("그룹관리에서 뭔가가 잘못되고 있는지 테스트하기 위한 라인")

        await self.channel_layer.group_discard(
            self.topic_name,
            self.channel_name
        )

    async def receive(self, text_data):
        ''' 웹소켓 연결 성공 후, 프론트에서 topid 수령'''
        received_id = json.loads(text_data)
        self.top_id = int(received_id['topId'])

        if TopicStorage.contains_topic_by_name(self.topic_name):
            current_topic = TopicStorage.retrieve_topic_by_name(self.topic_name)
            current_topic.add_count()
        else:
            current_topic = Topic(self.topic_name, self.top_id)
            TopicStorage.add_topic(current_topic)

    async def send_tweets(self, event):
        checked_tweets = []
        given_tweets = json.loads(event["tweets"])
        given_tweets = sorted(given_tweets, key=(lambda x: x['data']['id']))

        for tweet in given_tweets:
            if tweet["data"]["id"] > int(self.top_id):  # 제공한 트윗보다 더 이후의 트윗만 제공
                self.top_id = tweet["data"]["id"]
                checked_tweets.append(tweet)
        if checked_tweets:
            for tweet in checked_tweets:
                tweet['data']['id'] = str(tweet['data']['id'])
            await self.send(json.dumps({"tweets": checked_tweets}))

# @receiver(post_save, sender=Topic)
# def send_first_tweets(sender, instance, created, **kwargs):
#     if created:
#         RealtimeSender(instance.name, instance.top_id)
#
#
# class RealtimeSender:
#     def __init__(self, topic, top_id):
#         self.topic = topic
#         self.top_id = int(top_id)
#         self.keep_sending_tweets()
#
#     def keep_sending_tweets(self):
#         channel_layer = get_channel_layer()
#         serialized_tweets = get_realtime_tweet(self.topic, self.top_id)
#         try:
#             current_topic = Topic.objects.get(name=self.topic)
#             if serialized_tweets:
#                 self.top_id = serialized_tweets[0]['data']['id']
#                 async_to_sync(channel_layer.group_send)(
#                     self.topic, {
#                         "type": "send.tweets",
#                         "tweets": json.dumps(serialized_tweets),
#                     }
#                 )
#             else:
#                 print(self.topic, "에 대해 새로 생성된 트윗이 없다")
#
#             self.timer = threading.Timer(3, self.keep_sending_tweets)
#             self.timer.start()
#
#         except:
#             self.timer.cancel()
#             print("클라이언트 삭제가 성공적으로 반영되었고 실시간 함수는 중단될 것이다.")
#
#
# class FeedConsumer(WebsocketConsumer):
#     # 매번 부팅하기 전에 db 초기화 시킬것
#     def connect(self):
#         self.topic = self.scope['url_route']['kwargs']['topic']
#         self.accept()
#
#         async_to_sync(self.channel_layer.group_add)(
#             self.topic,
#             self.channel_name
#         )
#
#     def disconnect(self, close_code):
#         try:
#             current_topic = Topic.objects.get(name=self.topic)
#             current_topic.count -= 1
#             current_topic.save()
#             if current_topic.count == 0:
#                 current_topic.delete()
#         except:
#             print("그룹관리에서 뭔가가 잘못되고 있음")
#
#         async_to_sync(self.channel_layer.group_discard)(
#             self.topic,
#             self.channel_name
#         )
#
#     def receive(self, text_data):
#         ''' 웹소켓 연결 성공 후, 프론트에서 topid 수령'''
#         received_id = json.loads(text_data)
#         self.top_id = received_id['topId']
#         try:
#             current_topic = Topic.objects.get(name=self.topic)
#             current_topic.count += 1
#             current_topic.save()
#         except Topic.DoesNotExist:
#             Topic.objects.create(name=self.topic, top_id=self.top_id)
#
#     def send_tweets(self, event):
#         self.send(json.dumps({"tweets": event["tweets"]}))

#
# class FeedConsumer(WebsocketConsumer):
#
#     def connect(self):  # HANDSHAKING
#         self.topic = self.scope['url_route']['kwargs']['topic']
#         self.accept()  # CONNECT made
#
#     def disconnect(self, close_code):
#         ''' disconnect 되면 채널 이름을 삭제해서 timer 종료되도록 함.'''
#         self.channel_name = None
#         try:
#             self.timer.cancel()
#         except:
#             print("HANDSHAKING 후 connect에서 accept 되지 못하면 disconnect로 넘어오므로 timer는 존재하지 않음")
#
#     def receive(self, text_data):
#         ''' 웹소켓 연결 성공 후, 프론트에서 topid 수령'''
#         received_id = json.loads(text_data)
#         self.top_id = int(received_id['topId'])
#         self.keep_sending_tweets()  # 웹소켓이 연결되면 연결된 동안 최신 트윗 계속 내보내도록 하기
#
#     def keep_sending_tweets(self):
#         """ 여기서 최신 트윗 인수로 넣어서 그 이후의 트윗 가져오기. 3초마다 실행 """
#         serialized_tweets = get_realtime_tweet(self.topic, self.top_id)  # 여기서 인수로 top_id 넣고 SELECT WHERE id>top_id
#         """ 새롭게 생성된 트윗이 없다면 전송하지 않고 있는 경우에만 전송 """
#         if serialized_tweets:
#             ''' 웹소켓이 닫히더라도 timer가 돌고 있는 경우 이게 한번 더 실행됨'''
#             '''새로 생성되어 조회된 트윗이 있으면 가장 처음 트윗의 id 저장하고 전송함'''
#             self.top_id = serialized_tweets[0]['data']['id'] # 여기서 top_id를 업데이트해서 다음번 조회할 tweetid 세팅하기
#             self.send(json.dumps({"tweets":serialized_tweets}))
#         else:
#             print(self.channel_name, "해당 토픽에 새로 생성된 트윗이 없다")
#
#         if self.channel_name is not None:
#             self.timer = threading.Timer(3, self.keep_sending_tweets)
#             self.timer.start()
#         else:
#             print("채널 삭제 확인")
