from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from simulator.models import Category, Topic, Word

def catalog(request):
    categories = Category.objects.all()
    topics = Topic.objects.annotate(words_count=Count('words'))
    context = {
        'title': 'Практика',
        'topics': topics,
        'categories': categories,
    }
    return render(request, 'simulator/catalog.html', context=context)


def topic(request, topic_slug):
    # topic = Topic.objects.get(slug=topic_slug)
    topic = get_object_or_404(Topic, slug=topic_slug)
    words = Word.objects.filter(topic=topic)
    context = {
        'title': 'Перегляд слів',
        'words': words,
        'topic': topic,
    }
    return render(request, 'simulator/topic.html', context=context)



