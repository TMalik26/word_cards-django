from django.contrib import auth
from django.db.models import Count, Max
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from simulator.models import Topic
from users.forms import UserLoginForm, UserProfileForm, UserRegistrationForm


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserLoginForm()
    context = {
        'title': 'Авторизація',
        'form': form,
    }
    return render(request, 'users/login.html', context=context)


def user_logout(request):
    auth.logout(request)
    return redirect('main:index')


def profile(request):
    user = request.user
    user_topics = (
        Topic.objects
        .filter(game_sessions__user=user)
        .annotate(
            words_count=Count('words', distinct=True),
            progress=Max('game_sessions__result_percent')
        )
        .distinct()
    )
    if request.method == "POST":
        form = UserProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        form = UserProfileForm(instance=request.user)
    context = {
        'title': 'Акаунт',
        'form': form,
        'topics': user_topics,
    }
    return render(request, 'users/profile.html', context=context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserRegistrationForm()
    context = {
        'title': 'Реєстрація',
        'form': form,
    }
    return render(request, 'users/registration.html', context=context)