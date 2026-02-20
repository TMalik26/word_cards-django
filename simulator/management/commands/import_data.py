import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from simulator.models import Category, Topic, Word


class Command(BaseCommand):
    help = "Import data from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to JSON file (relative to project root)"
        )

    def handle(self, *args, **options):
        json_file = "simulator/fixtures/data.json"

        base_dir = Path(settings.BASE_DIR)
        file_path = base_dir / json_file

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for category_data in data:
            category, _ = Category.objects.get_or_create(
                name=category_data["category"],
                defaults={"slug": category_data["slug_category"]},
            )

            for topic_data in category_data["topics"]:
                topic, _ = Topic.objects.get_or_create(
                    name=topic_data["name"],
                    category=category,
                    defaults={"slug": topic_data["slug_topic"]},
                )

                for word_data in topic_data["words"]:
                    Word.objects.update_or_create(
                        slug=word_data["slug_word"],
                        topic=topic,
                        defaults={
                            "word_ukr": word_data["ukr"],
                            "word_eng": word_data["eng"],
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS("Data imported successfully!")
        )
