from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ('id',)

    def __str__(self):
        return self.name
    

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    category= models.ForeignKey(to=Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'topic'
        verbose_name = 'Тема'
        verbose_name_plural = 'Теми'
        ordering = ('id',)

    def __str__(self):
        return self.name
    
    # def words_count(self):
    #     return self.words.count()
    

class Word(models.Model):
    word_ukr = models.CharField(max_length=200, verbose_name='Українською')
    word_eng = models.CharField(max_length=200, verbose_name='Англійською')
    topic= models.ForeignKey(to=Topic, on_delete=models.CASCADE, related_name='words')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'word'
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        ordering = ('id',)

    def display_word_eng(self):
        return self.word_eng
    
    def display_word_ukr(self):
        return self.word_ukr