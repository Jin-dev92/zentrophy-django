from .models import Member
from rest_framework import serializers


class MemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class MemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['user_name', 'user_mail', 'phone_number', 'address']
