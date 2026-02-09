from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from game.forms import AnswerForm, ChooseDirectionForm
from game.models import GameAnswer, GameSession
from simulator.models import Topic, Word
from users.models import User


def prepare_game(request, topic_slug):
    # вычисляем юзера
    user = request.user
    # Узнаем что за тема вібрана пользователем чтобы список слов собрать
    topic = Topic.objects.get(slug=topic_slug)

    # Узнаем режим иссходя из квери-апроса
    mode = request.GET.get("mode")

    if mode == "mistakes":
        last_attempt = (
            GameSession.objects.filter(topic=topic, user=user).order_by("-id").first()
        )
        # ищем предыдущие ответы пользователя по теме
        # если нет предыдущей попытки или все ответы правильные:
        if not last_attempt:
            return redirect("simulator:topic", topic_slug=topic_slug)
        else:
            # формируем набор слов с is_correct=False
            words_list = (
                Word.objects.filter(
                    topic=topic,
                    gameanswer__session__user=user,
                    gameanswer__is_correct=False,
                )
                .distinct()
                .order_by("id")
            )
            # строка эквивалентная цыклу фор ниже
            # words_id = list( Word.objects.filter(topic=topic, game_session__answers__is_correct=False).order_by("id").values_list("id", flat=True))
            words_id = []
            for word in words_list:
                words_id.append(word.id)

            # вычисляем направление перевода как для прошлой игры с шибками
            direction = last_attempt.direction
            # сохраняем в джанго сессию три араметра: списой айди слов для практики, режим и направление перевода
            request.session["current_words"] = words_id
            request.session["mode"] = "mistakes"
            request.session["direction"] = direction

            # Создаем сессию игры чтобы передать ее в контроллер плей гейм:
            game_session = GameSession(
                topic=topic,
                user=user,
                direction=direction,
                mode="mistakes",
            )
            game_session.save()

            return redirect("game:play", session_id=game_session.id)

    else:
        # формируем список айдиников всех слов в теме
        words_list = Word.objects.filter(topic=topic).order_by("id")
        # строка эквивалентная цыклу фор ниже
        # words_id = list(Word.objects.filter(topic=topic).order_by("id").values_list("id", flat=True))
        words_id = []
        for word in words_list:
            words_id.append(word.id)

        # сохраняем в джанго сессию два араметра
        request.session["current_words"] = words_id
        request.session["mode"] = "full"

        # Redirect на страницу выбора направления перевода
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

    # По совету чата ГПТ чтоб юзер не зашел на страничку с юрл адреса
    # Проверяем, есть ли текущие слова в сессии
    if "current_words" not in request.session or not request.session["current_words"]:
        # Если нет, перенаправляем пользователя на страницу темы
        game_session = GameSession.objects.get(id=session_id)
        topic_slug = game_session.topic.slug
        return redirect("simulator:topic", topic_slug=topic_slug)
    # Конец совета чата ГПТ

    game_session = GameSession.objects.get(id=session_id)
    topic = game_session.topic
    # Получаем список айдишников слов из сохраненной сессии джанго в препар гейм
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
    }
    return render(request, "game/play.html", context=context)


def game_result(request, session_id):
    game_session = GameSession.objects.get(id=session_id)
    result_data = game_session.calculate_result()

    context = {
        "title": "Результати",
        "topic": game_session.topic,
        "user_result": result_data["percent"],
        "user_answers": result_data["total"],
        "correct_user_answers": result_data["correct"],
        "session": game_session,
    }
    return render(request, "game/result.html", context=context)
