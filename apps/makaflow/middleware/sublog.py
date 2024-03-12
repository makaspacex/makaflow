import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from apps.makaflow.models import SubLog
from apps.makaflow.tools import get_request_client
from common.models import XJUser as User
from common.tools import IP


class SubscribeLogMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        return None

    def process_response(self, request: WSGIRequest, response: HttpResponse):
        try:
            path = request.path
            path = path[1:] if path.startswith("/") else path
            if path != "api/v1/client/subscribe":
                return response

            success = False
            if isinstance(response, JsonResponse):
                resp = json.loads(response.content)
                if resp.get("code", 0):
                    success = True
            elif response.status_code == 200:
                success = True

            client_ip = IP.get_ip(request=request)
            client_type = get_request_client(request=request)
            token = request.GET.get("token", None)
            user = User.objects.filter(token=token).first()
            if not user:
                print(request.get_full_path())
            SubLog.objects.create(client=client_type, ip=client_ip, user=user)

        except Exception as e:
            pass
        return response
