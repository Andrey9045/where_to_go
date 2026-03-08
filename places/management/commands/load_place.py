import json
import os
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from places.models import Place, Image


class Command(BaseCommand):
    help = 'Загружает место из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON файлу')

    def load_json_data(self, json_file):
        try:
            if json_file.startswith(('http://', 'https://')):
                response = requests.get(json_file, timeout=30)
                response.raise_for_status()  # Проверяет HTTP статус
                return response.json()
            else:
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Ошибка загрузки по URL {json_file}: {e}')
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {json_file}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Ошибка парсинга JSON: {e}')

    def validate_data(self, data):
        required_fields = ['title', 'coordinates']
        for field in required_fields:
            if field not in data:
                raise CommandError(f'Отсутствует обязательное поле: {field}')

        if 'lat' not in data['coordinates'] or 'lng' not in data['coordinates']:
            raise CommandError('В поле coordinates должны быть lat и lng')

    def get_coordinates(self, data):
        try:
            lat = Decimal(str(data['coordinates']['lat']))
            lng = Decimal(str(data['coordinates']['lng']))
            return lat, lng
        except (InvalidOperation, TypeError, ValueError) as e:
            raise CommandError(f'Некорректные координаты: {e}')

    def create_or_update_place(self, data, lat, lng):
        short_desc = data.get('description_short', '')
        if len(short_desc) > 400:
            short_desc = short_desc[:397] + '...'

        defaults = {
            'short_description': short_desc,
            'long_description': data.get('description_long', ''),
            'lat': lat,
            'lng': lng,
        }

        try:
            place, created = Place.objects.get_or_create(
                title=data['title'],
                defaults=defaults
            )

            if not created:
                for field, value in defaults.items():
                    setattr(place, field, value)
                place.save()
                self.stdout.write(f'Обновлено существующее место: {place.title}')
            else:
                self.stdout.write(f'Создано новое место: {place.title}')

            return place
        except Exception as e:
            raise CommandError(f'Ошибка при сохранении места: {e}')

    def download_image(self, img_url, position, place):
        try:
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                self.stdout.write(
                    self.style.WARNING(f'URL {img_url} не является изображением (content-type: {content_type})')
                )
                return False

            parsed = urlparse(img_url)
            filename = os.path.basename(parsed.path)
            if not filename or not os.path.splitext(filename)[1]:
                filename = f'image_{position}.jpg'
            elif not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                base = os.path.splitext(filename)[0]
                filename = f'{base}.jpg'
            image = Image.objects.create(place=place, position=position)
            image.image.save(filename, ContentFile(response.content), save=True)
            
            self.stdout.write(f'   Загружено изображение {position}: {filename}')
            return True
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'   Ошибка скачивания изображения {position}: {e}')
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'   Ошибка сохранения изображения {position}: {e}')
            )
            return False
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            self.stdout.write(f'Загрузка данных из: {json_file}')
            data = self.load_json_data(json_file)
            self.validate_data(data)
            lat, lng = self.get_coordinates(data)
            with transaction.atomic():
                place = self.create_or_update_place(data, lat, lng)
                old_images_count = place.images.count()
                if old_images_count > 0:
                    place.images.all().delete()
                    self.stdout.write(f'Удалено старых изображений: {old_images_count}')
                img_urls = data.get('imgs', [])
                if img_urls:
                    self.stdout.write(f'Загрузка {len(img_urls)} изображений:')
                    successful = 0
                    for position, img_url in enumerate(img_urls, start=1):
                        if self.download_image(img_url, position, place):
                            successful += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Загружено изображений: {successful}/{len(img_urls)}')
                    )
                else:
                    self.stdout.write(self.style.WARNING('Нет изображений для загрузки'))

            self.stdout.write(
                self.style.SUCCESS(f'Успешно завершено: {place.title}')
            )
            
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
            raise  
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nПрервано пользователем'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Непредвиденная ошибка: {type(e).__name__}: {e}')
            )
            raise