

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.http.response import HttpResponse, Http404
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from apps.makaflow import configs
from apps.makaflow import urls as app_urls
from apps.makaflow.models import SubLog
from common.tools import IP
from apps.makaflow.tools import get_request_client
from common.models import XJUser as User


class SubscribeLogMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):

        try:
            path = request.path
            path = path[1:] if path.startswith("/") else path
            if path != "api/v1/client/subscribe":
                return None
            client_ip = IP.get_ip(request=request)
            client_type = get_request_client(request=request)
            token = request.GET.get("token",None)
            user = None
            if token:
                user = User.objects.filter(token=token).first()
            SubLog.objects.create(client=client_type,ip=client_ip,user=user)

        except Exception as e:
            pass

        return None

    def process_response(self, request: WSGIRequest, response: HttpResponse):
        if "page" in request.path.split("/"):
            pass
        return response