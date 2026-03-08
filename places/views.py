import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from places.models import Place


def index(request):
    places = Place.objects.all()
    features = []
    for place in places:
        feature = {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [float(place.lng), float(place.lat)]
          },
          "properties": {
            "title": place.title,
            "placeId": place.id,
            "detailsUrl": reverse('place_detail', args=[place.id])
          }
        }
        features.append(feature)
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return render(request, 'index.html', {'places_geojson': geojson})

def place_detail(request, place_id):
    place = get_object_or_404(Place.objects.prefetch_related('images'), id=place_id)
    images = place.images.all().order_by('position')
    place_context = {
        "title" : place.title,
        "imgs" : [image.image.url for image in images],
        "short_description" : place.short_description,
        "long_description" : place.long_description,
    }

    return JsonResponse(place_context, json_dumps_params={'ensure_ascii': False})