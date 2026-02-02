from django.db import models

from simulator.models import Topic, Word
from users.models import User

class GameSession(models.Model):
    topic = models.ForeignKey(to=Topic, on_delete=models.CASCADE, related_name='game_sessions')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='game_sessions')

    DIRECTION_CHOICES = [
        ('eng_ukr', 'Англійська → Українська'),
        ('ukr_eng', 'Українська → Англійська'),
    ]

    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    current_index = models.PositiveIntegerField(default=0)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'game_session'
        verbose_name = 'Сессія гри'
        verbose_name_plural = 'Сессії гри'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} - {self.topic}'
    

class GameAnswer(models.Model):
    session = models.ForeignKey(to=GameSession, on_delete=models.CASCADE, related_name='answers')
    word = models.ForeignKey(to=Word, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=100, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'word')
        db_table = 'game_answer'
        verbose_name = 'Відповідь'
        verbose_name_plural = 'Відповіді'
        ordering = ('answered_at',)

    def __str__(self):
        return f'{self.word} - {self.user_answer}'
