import json
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from places.models import Place
from django.http import JsonResponse


def index(request):
    places = Place.objects.all()
    features = []
    for place in places:
        print(f"Processing place: {place.id}, {place.title}, lng: {place.lng}, lat: {place.lat}")
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
    print(f"Generated GeoJSON: {json.dumps(geojson, indent=2)}")
#    geojson_str = json.dumps(geojson, ensure_ascii=True)
    return render(request, 'index.html', {'places_geojson': geojson})

def place_detail(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    images = place.images.all().order_by('position')
    data = {
        "title" : place.title,
        "imgs" : [image.image.url for image in images],
        "description_short" : place.description_short,
        "description_long" : place.description_long,
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})