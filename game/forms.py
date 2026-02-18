from django import forms

from game.models import GameAnswer, GameSession


class ChooseDirectionForm(forms.ModelForm):
    class Meta:
        model = GameSession
        fields = ["direction"]
    direction = forms.ChoiceField(
        choices=GameSession.DIRECTION_CHOICES,
        widget=forms.RadioSelect,
        label="Оберіть напрям перекладу"
    )


class AnswerForm(forms.ModelForm):
    class Meta:
        model = GameAnswer
        fields = ["user_answer"]
    user_answer = forms.CharField(max_length=100, required=False)