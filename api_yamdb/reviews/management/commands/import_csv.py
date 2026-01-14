import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файлов в базу данных'

    def handle(self, *args, **options):
        files_to_methods = [
            ('users.csv', self.import_users),
            ('category.csv', self.import_categories),
            ('genre.csv', self.import_genres),
            ('titles.csv', self.import_titles),
            ('review.csv', self.import_reviews),
            ('comments.csv', self.import_comments),
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

    def import_users(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                row_id = row.pop('id')
                user, created = User.objects.update_or_create(
                    id=row_id,
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row.get('role', 'user'),
                        'bio': row.get('bio', ''),
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                    }
                )

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
                row['category_id'] = row.pop('category')
                Title.objects.get_or_create(**row)

    def import_reviews(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                try:
                    user = User.objects.get(id=row['author'])
                    title = Title.objects.get(id=row['title_id'])
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Пользователь {row['author']} не найден!"
                            )
                        )
                    continue
                except Title.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Тайтл {row['title_id']} не найден!"
                            )
                        )
                    continue

                row_id = row.pop('id')
                row['author_id'] = row.pop('author')
                Review.objects.update_or_create(id=row_id, defaults=row)

    def import_comments(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                try:
                    user = User.objects.get(id=row['author'])
                    review = Review.objects.get(id=row['review_id'])
                except User.DoesNotExist(
                    f'{user} или {review} еще не были созданы!'
                ):
                    continue
                except Review.DoesNotExist(
                    f'{user} или {review} еще не были созданы!'
                ):
                    continue

                row_id = row.pop('id')
                row['author_id'] = row.pop('author')
                Comment.objects.update_or_create(id=row_id, defaults=row)

    def import_genre_titles(self, file_name):
        reader = self.get_reader(file_name)
        if reader:
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
