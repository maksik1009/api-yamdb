import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, Title  # Comment, Review, User


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файлов в базу данных'

    def handle(self, *args, **options):
        files_to_methods = [
            # ('users.csv', self.import_users),
            ('category.csv', self.import_categories),
            ('genre.csv', self.import_genres),
            ('titles.csv', self.import_titles),
            # ('reviews.csv', self.import_reviews),
            # ('comments.csv', self.import_comments),
            ('genre_title.csv', self.import_genre_titles),
        ]

        for file_name, method in files_to_methods:
            self.stdout.write(f'Загрузка {file_name}...')
            method(file_name)

        self.stdout.write(self.style.SUCCESS('Импорт успешно завершен!'))

    def get_reader(self, file_name):
        """Метод открывает путь CSV файла и возвращает DictReader."""
        path = os.path.join(settings.BASE_DIR, 'static', 'data', file_name)

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {path}'))
            return None

        csv_file = open(path, encoding='utf-8')
        return csv.DictReader(csv_file)

    # def import_users(self, file_name):
    #     reader = self.get_reader(file_name)
    #     if reader:
    #         for row in reader:
    #             User.objects.get_or_create(**row)

    def import_categories(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                Category.objects.get_or_create(**row)

    def import_genres(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                Genre.objects.get_or_create(**row)

    def import_titles(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                # В CSV 'category', а в БД колонка 'category_id'
                row['category_id'] = row.pop('category')
                Title.objects.get_or_create(**row)

    # def import_reviews(self, file_name):
    #     reader = self.get_reader(file_name)
    #     if reader:
    #         for row in reader:
    #             # В CSV 'author', а в БД колонка 'author_id'
    #             row['author_id'] = row.pop('author')
    #             Review.objects.get_or_create(**row)

    # def import_comments(self, file_name):
    #     reader = self.get_reader(file_name)
    #     if reader:
    #         for row in reader:
    #             # В CSV 'author', а в БД колонка 'author_id'
    #             row['author_id'] = row.pop('author')
    #             Comment.objects.get_or_create(**row)

    def import_genre_titles(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
