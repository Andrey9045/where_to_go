import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
from where_to_go.models import Place, Image  # ← ИЗМЕНИТЕ ЭТУ СТРОКУ
import json
import os
from urllib.parse import urlparse
from decimal import Decimal 

class Command(BaseCommand):
    help = 'Загружает место из JSON файла'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON файлу')
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            if json_file.startswith(('http://', 'https://')):
                data = requests.get(json_file).json()
            else:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)


            short_desc = data.get('description_short', '')
            if len(short_desc) > 400:
                short_desc = short_desc[:397] + '...'
            
            lat = Decimal(str(data['coordinates']['lat']))
            lng = Decimal(str(data['coordinates']['lng']))
            

            place, created = Place.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description_short': short_desc,
                    'description_long': data.get('description_long', ''),
                    'lat': lat,
                    'lng': lng,
                }
            )
            
            if not created:
                place.lat = lat
                place.lng = lng
                place.save()
            

            place.images.all().delete()
            
            for position, img_url in enumerate(data.get('imgs', []), start=1):
                try:
                    response = requests.get(img_url, timeout=10)
                    
                    parsed = urlparse(img_url)
                    filename = os.path.basename(parsed.path)
                    if not filename:
                        filename = f'image_{position}.jpg'
                    
                    image = Image.objects.create(place=place, position=position)
                    image.image.save(filename, ContentFile(response.content), save=True)
                    
                except Exception:
                    pass
            
            self.stdout.write(self.style.SUCCESS(f'Завершено: {place.title}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))