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

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    preview.short_description = "Превью"


@admin.register(Place)
class PlaceAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ('id', 'title', 'short_description', 'long_description', 'coordinates')
    list_display_links = ('title', 'short_description', 'long_description')
    # Явно указываем стандартный шаблон для списка
    change_list_template = 'admin/change_list.html'  # ← ДОБАВЬТЕ ЭТУ СТРОКУ!

    # Явно указываем стандартный шаблон для формы редактирования
    change_form_template = 'admin/change_form.html'

    def short_description(self, obj):
        if obj.description_short:
        	return obj.description_short[:30]+ "..." if len(obj.description_short)>30 else obj.description_short
        return "-"
    short_description.short_description = "Короткое описание"

    def long_description(self, obj):
        if obj.description_long:
            return obj.description_long[:30] + "..." if len(obj.description_long)>30 else obj.description_long
        return "-"
    long_description.short_description = "Полное описание"

    def coordinates(self, obj):
        return f"Долгота: {obj.lng}, Широта: {obj.lat}"
    coordinates.short_description = "Координаты"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('position', 'place_title', 'image_preview')
    list_display_links = ('image_preview',)

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
