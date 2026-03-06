from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Place, Image
from tinymce.widgets import TinyMCE
from adminsortable2.admin import SortableTabularInline
from adminsortable2.admin import SortableAdminMixin


class ImageInline(SortableTabularInline):
    model = Image
    extra = 3
    fields = ('image', 'preview')
    readonly_fields = ('preview',)
    template = 'admin/edit_inline/tabular.html'
    raw_id_fields = ('place',) 

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    preview.short_description = "Превью"


@admin.register(Place)
class PlaceAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = (
        'id',
        'title',
        'short_description',
        'long_description',
        'coordinates'
    )
    list_display_links = ('title', 'short_description', 'long_description')

    def short_description(self, obj):
        if obj.description_short:
            text = obj.description_short
            if len(text) > 30:
                return text[:30] + "..."
            else:
                return text
        else:
            return "-"
    short_description.short_description = "Короткое описание"

    def long_description(self, obj):
        if obj.description_long:
            text = obj.description_long
            if len(text) > 30:
                return text[:30] + "..."
            else:
                return text
        else:
            return "-"
    long_description.short_description = "Полное описание"

    def coordinates(self, obj):
        return f"Долгота: {obj.lng}, Широта: {obj.lat}"
    coordinates.short_description = "Координаты"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('position', 'place_title', 'image_preview')
    list_display_links = ('image_preview',)
    raw_id_fields = ['place']
    def place_title(self, obj):
        return obj.place.title
    place_title.short_description = "Место"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"
    image_preview.allow_tags = True
# Register your models here.
