from django.contrib import admin

from simulator.models import Category, Topic, Word


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',)
    }
    list_display = ['name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',)
    }
    list_display = ['name', 'category']
    list_editable = ['category']
    search_fields = ['name', 'category']
    list_filter = ['name', 'category']


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('word_eng',)
    }
    list_display = ['word_ukr', 'word_eng', 'topic']
    list_editable = ['word_eng', 'topic']
    search_fields = ['word_ukr', 'word_eng', 'topic']
    list_filter = ['topic']