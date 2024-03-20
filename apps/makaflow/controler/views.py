from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from common.tools.model_tools import get_json_model


def index_page(request: WSGIRequest):
    context = {}
    context["title"] = "首页"
    context["page_name"] = "index"

    try:
        data = {}
        context.update(data)
    except Exception as e:
        pass

    return render(request, template_name="makaflow/index.html", context=context)
