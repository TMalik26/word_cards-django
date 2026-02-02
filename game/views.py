from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from game.forms import AnswerForm, ChooseDirectionForm
from game.models import GameAnswer, GameSession
from simulator.models import Topic, Word
from users.models import User


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
    game_session = GameSession.objects.get(id=session_id)
    topic = game_session.topic
    words_list = Word.objects.filter(topic=topic).order_by("id")

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
        form = AnswerForm(data=request.POST)

        if action == "skip":
            game_answer = GameAnswer(
                session=game_session,
                word=word_to_answer,
                user_answer="",
                is_correct=False,
            )
            game_answer.save()

        elif action == "answer" and form.is_valid():
            user_answer = request.POST["user_answer"].strip()
            is_correct = user_answer.lower() == correct_word.lower()
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
    }
    return render(request, "game/play.html", context=context)


def game_result(request, session_id):
    game_session = GameSession.objects.get(id=session_id)
    topic = game_session.topic
    answers_qs  = GameAnswer.objects.filter(session=game_session)
    total_answers = answers_qs.count()
    correct_answers = answers_qs.filter(is_correct=True).count()
    if total_answers > 0:
        user_result = round((correct_answers / total_answers) * 100)
    else:
        user_result = 0
    context = {
        "title": "Результати",
        "topic": topic,
        "user_result": user_result,
        "user_answers": total_answers,
        "correct_user_answers": correct_answers,
    }
    return render(request, "game/result.html", context=context)
