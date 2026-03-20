import json
import os
import django

# Setting up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'word_cards.settings')
django.setup()

from simulator.models import Category, Topic, Word

def load_data_from_json(file_path):
    """
    Loads data from a JSON file and populates the database.
    
    Example JSON structure:
    {
        "category": "Everyday Life",
        "slug_category": "everyday-life",
        "topics": [
            {
                "name": "Morning Routines",
                "slug_topic": "morning-routines",
                "words": [
                    {"ukr": "Вставати", "eng": "Wake up", "slug_word": "wake-up"},
                    ...
                ]
            }
        ]
    }
    """
    if not os.path.exists(file_path):
        print(f"❌ Файл не знайдено: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. Створити категорію
        category_data = data.get('category', 'Uncategorized')
        category_slug = data.get('slug_category', 'uncategorized')
        
        category, category_created = Category.objects.get_or_create(
            slug=category_slug,
            defaults={'name': category_data}
        )
        
        status = "✅ створена" if category_created else "⚠️ вже існує"
        print(f"Категорія '{category_data}' {status}")
        
        # 2. Обробити всі теми (topics)
        for topic_data in data.get('topics', []):
            topic_name = topic_data.get('name', 'Unknown')
            topic_slug = topic_data.get('slug_topic', 'unknown')
            words = topic_data.get('words', [])
            
            # 2.1 Створити тему
            topic, topic_created = Topic.objects.get_or_create(
                slug=topic_slug,
                category=category,
                defaults={'name': topic_name}
            )
            
            status = "✅ створена" if topic_created else "⚠️ вже існує"
            print(f"  └─ Тема '{topic_name}' {status}")
            
            # 2.2 Додати всі слова для цієї теми
            words_count = 0
            for word_data in words:
                ukr_word = word_data.get('ukr', '')
                eng_word = word_data.get('eng', '')
                word_slug = word_data.get('slug_word', '')
                
                # Перевірити чи слово вже існує для цієї теми
                word, word_created = Word.objects.get_or_create(
                    topic=topic,
                    slug=word_slug,
                    defaults={
                        'word_ukr': ukr_word,
                        'word_eng': eng_word,
                    }
                )
                
                if word_created:
                    words_count += 1
                    print(f"      ├─ ✅ Слово додано: '{ukr_word}' → '{eng_word}'")
                else:
                    print(f"      ├─ ⚠️ Слово вже існує: '{ukr_word}' → '{eng_word}'")
            
            print(f"      └─ Всього додано слів для теми: {words_count}")
        
        print("\n✅ Усі дані успішно завантажено до БД!")
        
    except json.JSONDecodeError as e:
        print(f"❌ Помилка парсинга JSON: {e}")
    except Exception as e:
        print(f"❌ Помилка при завантаженні: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    json_file = 'data/data.json'
    load_data_from_json(json_file)