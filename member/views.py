# from django.shortcuts import render
from .models import Member
from rest_framework import viewsets

# Create your views here.
from .serializer import MemberListSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberListSerializer

# class MemberCreate(generics.CreateAPIView):
#     queryset = Member.objects.all()
#     serializer_class = MemberCreateSerializer
