from rest_framework import serializers
from collections import OrderedDict


class AttachmentSerializer(serializers.Serializer):
    media_keys = serializers.ListField(
        child=serializers.CharField()
    )

    def to_representation(self, instance):
        result = super(AttachmentSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    username = serializers.CharField()
    profile_image_url = serializers.CharField()
    verified = serializers.BooleanField()

    def to_representation(self, instance):
        result = super(UserSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class UrlSerailizer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    url = serializers.CharField()
    expanded_url = serializers.CharField()
    display_url = serializers.CharField()
    unwound_url = serializers.CharField()

    def to_representation(self, instance):
        result = super(UrlSerailizer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class MentionSerailizer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    username = serializers.CharField()

    def to_representation(self, instance):
        result = super(MentionSerailizer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class TagSerailizer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    tag = serializers.CharField()

    def to_representation(self, instance):
        result = super(TagSerailizer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class EntitySerializer(serializers.Serializer):
    urls = UrlSerailizer(many=True)
    mentions = MentionSerailizer(many=True)
    hashtags = TagSerailizer(many=True)
    cashtags = TagSerailizer(many=True)

    def to_representation(self, instance):
        result = super(EntitySerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class PublicMetricSerializer(serializers.Serializer):
    retweet_count = serializers.IntegerField()
    reply_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    quote_count = serializers.IntegerField()

    def to_representation(self, instance):
        result = super(PublicMetricSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])

class ReferencedTweetSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()

    def to_representation(self, instance):
        result = super(ReferencedTweetSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class TweetSerializer(serializers.Serializer):
    id = serializers.CharField()
    author_id = serializers.CharField()
    message = serializers.CharField()
    conversation_id = serializers.CharField()
    possibly_sensitive = serializers.BooleanField()
    attachments = AttachmentSerializer()
    reply_settings = serializers.CharField()
    source = serializers.CharField()
    public_metrics = PublicMetricSerializer()
    entities = EntitySerializer()
    referenced_tweets = ReferencedTweetSerializer(many=True)
    place_id = serializers.CharField()
    lang = serializers.CharField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
        result = super(TweetSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class MediaSerializer(serializers.Serializer):
    type = serializers.CharField()
    media_key = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    view_count = serializers.CharField()

    def to_representation(self, instance):
        result = super(MediaSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class PlaceSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    id = serializers.CharField()
    country = serializers.CharField()
    country_code = serializers.CharField()
    name = serializers.CharField()
    place_type = serializers.CharField()

    def to_representation(self, instance):
        result = super(PlaceSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class IncludeSerializer(serializers.Serializer):
    tweets = TweetSerializer(many=True)
    users = UserSerializer(many=True)
    media = MediaSerializer(many=True)
    places = PlaceSerializer(many=True)

    def to_representation(self, instance):
        result = super(IncludeSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


class TweetsSerializer(serializers.Serializer):
    topic = serializers.CharField()
    datehour = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    id = serializers.IntegerField()
    message = serializers.CharField()
    attachments = AttachmentSerializer()
    author_id = serializers.CharField()
    conversation_id = serializers.CharField()
    entities = EntitySerializer()
    in_reply_to_user_id = serializers.CharField()
    possibly_sensitive = serializers.BooleanField()
    public_metrics = PublicMetricSerializer()
    referenced_tweets = ReferencedTweetSerializer(many=True)
    reply_settings = serializers.CharField()
    source = serializers.CharField()
    lang = serializers.CharField()
    place_id = serializers.CharField()
    includes = IncludeSerializer()
    stored_at = serializers.DateTimeField()

    def to_representation(self, instance):
        result = super(TweetsSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None and check_empty(result[key])])


def check_empty(val):
    if isinstance(val, list):
        if not val[0]:
            return False

    if isinstance(val, dict):
        if not val:
            return False

    return True
