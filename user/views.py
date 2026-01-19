from django.shortcuts import render


def login(request):
    context = {
        'title': 'Вхід',
    }
    return render(request, 'user/login.html', context=context)

def logout(request):
    context = {
        'title': 'Вихід',
    }
    return render(request, 'user/login.html', context=context)

def registration(request):
    context = {
        'title': 'Реєстрація',
    }
    return render(request, 'user/registration.html', context=context)

def profile(request):
    context = {
        'title': 'Акаунт',
    }
    return render(request, 'user/profile.html', context=context)