from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from game.forms import AnswerForm, ChooseDirectionForm
from game.models import GameAnswer, GameSession
from simulator.models import Topic, Word
from users.models import User


def prepare_game(request, topic_slug):
    user = request.user
    topic = Topic.objects.get(slug=topic_slug)
    mode = request.GET.get("mode")
    if mode == "mistakes":
        last_attempt = (
            GameSession.objects.filter(topic=topic, user=user)
            .order_by("-id")
            .first()
        )
        if not last_attempt:
            return redirect("simulator:topic", topic_slug=topic_slug)
        mistakes_filter = Q(
            gameanswer__session__user=user,
            gameanswer__is_correct=False
        )
        words_id = list(
            Word.objects.filter(topic=topic).filter(mistakes_filter)
            .distinct()
            .order_by("id")
            .values_list("id", flat=True)
        )
        if not words_id:
            return redirect("simulator:topic", topic_slug=topic_slug)
        direction = last_attempt.direction
        request.session["current_words"] = words_id
        request.session["mode"] = "mistakes"
        request.session["direction"] = direction
        game_session = GameSession(
            topic=topic,
            user=user,
            direction=direction,
            mode="mistakes",
        )
        game_session.save()
        return redirect("game:play", session_id=game_session.id)

    else:
        words_id = list(
            Word.objects.filter(topic=topic)
            .order_by("id")
            .values_list("id", flat=True)
        )
        if not words_id:
            return redirect("simulator:topic", topic_slug=topic_slug)
        request.session["current_words"] = words_id
        request.session["mode"] = "full"
        return redirect("game:direction", topic_slug=topic_slug)


def choose_direction(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    user = request.user
    if request.method == "POST":
        form = ChooseDirectionForm(data=request.POST)
        if form.is_valid():
            direction = request.POST["direction"]
            game_session = GameSession(direction=direction, topic=topic, user=user)
            game_session.save()
            return redirect("game:play", session_id=game_session.id)
    else:
        form = ChooseDirectionForm()
    context = {
        "title": "Практика",
        "form": form,
        "topic": topic,
    }
    return render(request, "game/choose_direction.html", context=context)


def play_game(request, session_id):
    if "current_words" not in request.session or not request.session["current_words"]:
        game_session = GameSession.objects.get(id=session_id)
        topic_slug = game_session.topic.slug
        return redirect("simulator:topic", topic_slug=topic_slug)
    game_session = GameSession.objects.get(id=session_id)
    topic = game_session.topic
    words_id = request.session["current_words"]
    words_list = Word.objects.filter(id__in=words_id).order_by("id")
    if game_session.is_finished or game_session.current_index >= len(words_list):
        game_session.is_finished = True
        game_session.save()
        return redirect("game:result", session_id=game_session.id)
    word_to_answer = words_list[game_session.current_index]
    if game_session.direction == "eng_ukr":
        shown_word = word_to_answer.display_word_eng()
        correct_word = word_to_answer.word_ukr
    else:
        shown_word = word_to_answer.display_word_ukr()
        correct_word = word_to_answer.word_eng
    if request.method == "POST":
        action = request.POST.get("action")
        form = AnswerForm(request.POST)
        if form.is_valid():
            if action == "skip":
                game_answer = GameAnswer(
                    session=game_session,
                    word=word_to_answer,
                    user_answer="",
                    is_correct=False,
                )
                game_answer.save()
            elif action == "answer":
                user_answer = form.cleaned_data["user_answer"].strip()
                is_correct = (
                    user_answer.lower() == correct_word.lower()
                    if user_answer
                    else False
                )
                game_answer = GameAnswer(
                    session=game_session,
                    word=word_to_answer,
                    user_answer=user_answer,
                    is_correct=is_correct,
                )
                game_answer.save()
            game_session.current_index += 1
            if game_session.current_index >= len(words_list):
                game_session.is_finished = True
            game_session.save()
            if game_session.is_finished:
                return redirect("game:result", session_id=game_session.id)
            else:
                return redirect("game:play", session_id=game_session.id)
    else:
        form = AnswerForm()
    context = {
        "title": f"Режим навчання - {topic.name}",
        "form": form,
        "word": shown_word,
        "session": game_session,
        "current_word": game_session.current_index + 1,
        "total_words": len(words_list),
    }
    return render(request, "game/play.html", context=context)


def game_result(request, session_id):
    game_session = GameSession.objects.get(id=session_id)
    result_data = game_session.calculate_result()
    wrong_words = result_data["total"] - result_data["correct"]
    context = {
        "title": "Результати",
        "topic": game_session.topic,
        "user_result": result_data["percent"],
        "user_answers": result_data["total"],
        "correct_user_answers": result_data["correct"],
        "session": game_session,
        "wrong_words": wrong_words,
    }
    return render(request, "game/result.html", context=context)
