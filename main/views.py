from django.shortcuts import render

def index(request):
    context= {
        'title': 'Головна сторінка'
    }
    return render(request, 'main/index.html', context=context)