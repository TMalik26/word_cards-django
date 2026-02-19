import json
from django.core.management.base import BaseCommand
from simulator.models import Category, Topic, Word


class Command(BaseCommand):
    help = "Import categories, topics and words from JSON"


    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str)


    def handle(self, *args, **options):
        with open(options["json_file"], "r", encoding="utf-8") as f:
            data = json.load(f)

        for category_data in data:
            category, _ = Category.objects.get_or_create(
                name=category_data["category"],
                defaults={"slug": category_data["slug_category"]}
            )

            for topic_data in category_data["topics"]:
                topic, _ = Topic.objects.get_or_create(
                    name=topic_data["name"],
                    category=category,
                    defaults={"slug": topic_data["slug_topic"]}
                )

                for word_data in topic_data["words"]:
                    Word.objects.get_or_create(
                        word_ukr=word_data["ukr"],
                        word_eng=word_data["eng"],
                        topic=topic,
                        defaults={"slug": word_data["slug_word"]}
                    )

        self.stdout.write(self.style.SUCCESS("Data imported successfully!"))
