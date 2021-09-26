import os
from urllib.parse import scheme_chars
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import *

class MessageNoticeView(APIView):
    def get (self, request):
        """
        Get the message notice.
        """
        notice = MessageNotice.objects.all().first()
        serializer = MessageNoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post (self, request):
        """
        Posting a new message notice will delete all prior message notices
        """
        old_notices = MessageNotice.objects.all()
        old_notices.delete()

        serializer = MessageNoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
