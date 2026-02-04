from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from game.models import GameSession
from simulator.models import Category, Topic, Word

def catalog(request):
    user = request.user
    categories = Category.objects.all()

    topics = Topic.objects.annotate(words_count=Count('words'))

    selected_categories = request.GET.getlist("category")
    progress_filters = request.GET.getlist("progress")
    order_by = request.GET.get("order_by")

    if selected_categories:
        topics = topics.filter(category__slug__in=selected_categories)

    topic_progress = {}
    for topic in topics:
        session = GameSession.objects.filter(user=user, topic=topic).first()
        if session:
            topic_progress[topic.id] = session.result_percent
        else:
            topic_progress[topic.id] = 0

    if progress_filters:
        filtered_topics = []
        for topic in topics:
            percent = topic_progress[topic.id]
            if "new" in progress_filters and percent == 0:
                filtered_topics.append(topic)
            elif "failed" in progress_filters and 0 < percent < 100:
                filtered_topics.append(topic)
            elif "done" in progress_filters and percent == 100:
                filtered_topics.append(topic)
        topics = filtered_topics

    else:
        topics = list(topics)

    if order_by == '-progress':
        topics.sort(key=lambda t: topic_progress[topic.id], reverse=True)
    else:
        topics.sort(key=lambda t: t.name) 

    context = {
        'title': 'Практика',
        'topics': topics,
        'categories': categories,
        'selected_categories': selected_categories,
        'progress_filters': progress_filters,
        'order_by': order_by,
        'topic_progress': topic_progress,
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



