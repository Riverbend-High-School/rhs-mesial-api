from rest_framework import serializers

from .models import *

class MessageNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageNotice
        fields = '__all__'

class LightNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LightNotice
        fields = '__all__'

class ActiveSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        fields = ['id', 'message', 'path']

