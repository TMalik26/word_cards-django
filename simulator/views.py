from django.db.models import Q, Count, Max
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .management.commands.import_data import Command

from game.models import GameSession
from simulator.models import Category, Topic, Word


def catalog(request):
    user = request.user
    categories = Category.objects.all()
    topics = Topic.objects.all().annotate(
        words_count=Count('words', distinct=True),
        progress=Max('game_sessions__result_percent', filter=Q(game_sessions__user=user))
    )
    selected_categories = request.GET.getlist("category")
    progress_filters = request.GET.getlist("progress")
    order_by = request.GET.get("order_by")
    if selected_categories:
        topics = topics.filter(category__slug__in=selected_categories)
    if progress_filters:
        progress_query = Q()
        if "new" in progress_filters:
            progress_query |= Q(progress__isnull=True) | Q(progress=0)
        if "failed" in progress_filters:
            progress_query |= Q(progress__gt=0, progress__lt=100)
        if "done" in progress_filters:
            progress_query |= Q(progress=100)
        topics = topics.filter(progress_query)
    if order_by == "-progress":
        topics = topics.order_by('-progress')
    else:
        topics = topics.order_by('name')
    context = {
        "title": "Практика",
        "topics": topics,
        "categories": categories,
        "selected_categories": selected_categories,
        "progress_filters": progress_filters,
        "order_by": order_by,
    }
    return render(request, "simulator/catalog.html", context=context)


def topic(request, topic_slug):
    user = request.user
    topic = get_object_or_404(Topic, slug=topic_slug)
    words = Word.objects.filter(topic=topic)
    best_attempt = GameSession.objects.filter(
        topic=topic,
        user=user,
        is_finished=True
    ).aggregate(best_percent=Max('result_percent'))['best_percent'] or 0
    best_attempt = int(best_attempt)
    context = {
        "title": "Перегляд слів",
        "words": words,
        "topic": topic,
        "percent": best_attempt,
    }
    return render(request, "simulator/topic.html", context=context)


@csrf_exempt
def import_data_view(request):
    Command().handle("data/data.json")
    return HttpResponse("Data imported successfully!")


def test_data_view(request):
    categories = Category.objects.all()
    topics = Topic.objects.all()
    words = Word.objects.all()
    return HttpResponse(
        f"Categories: {categories.count()}, Topics: {topics.count()}, Words: {words.count()}"
    )