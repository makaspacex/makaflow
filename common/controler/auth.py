from django.contrib.auth import authenticate
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

# from django.contrib.auth.models import User
from common.models import XJUser as User


def signin_page(request: WSGIRequest):
    context = {}
    context['title'] = '登录'
    context['page_name'] = 'signin'

    if request.session.get('user', None):
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'auth/signin.html', context)
    name = request.POST.get('name')
    password = request.POST.get('password')

    user = authenticate(request, username=name, password=password)
    if user is not None:
        request.session['user'] = name
        request.session['_auth_user_id'] = user.id
    else:
        context['error'] = "用户名或密码错误"
        return render(request, 'auth/signin.html', context)
    return redirect('/')


def signup_page(request: WSGIRequest):
    context = {}
    context['title'] = '注册'
    context['page_name'] = 'signup'
    if request.session.get('user', None):
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'auth/signup.html', context)
    # 建立新账户
    name = request.POST.get('name')
    email = request.POST.get('email')
    passwd = request.POST.get('password')
    res = User.objects.filter(username=name).first()
    if res:
        context['error'] = "用户已经存在"
        return render(request, 'auth/signup.html', context)

    user = User.objects.create_user(name, email, passwd)

    user.save()
    request.session['user'] = name
    request.session['_auth_user_id'] = user.id
    return redirect('/')


def signout(request: WSGIRequest):
    request.session['user'] = None
    request.session['_auth_user_id'] = -1

    return redirect('/')
