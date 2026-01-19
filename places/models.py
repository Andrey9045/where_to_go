from django.db import models
from tinymce.models import HTMLField

class Place(models.Model):
    title = models.CharField(
        verbose_name="Название локации",
        max_length=200
    )
    description_short = models.CharField(
        verbose_name="Краткое описание",
        max_length=400,
        blank=True,
        default=""
    )
    description_long = HTMLField(verbose_name="Полное описание")
    lng = models.DecimalField(
        verbose_name="Долгота",
        max_digits=17,
        decimal_places=14,
        blank=True
    )
    lat = models.DecimalField(
        verbose_name="Широта",
        max_digits=17,
        decimal_places=14
    )

    class Meta:
        ordering = ['title']
        verbose_name = "Место"
        verbose_name_plural = "Места"


class Image(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Место",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="pictures/%Y/%m/%d/",
        max_length=100,
    )
    position = models.PositiveIntegerField(
        verbose_name="Позиция",
        default=0,
        db_index=True,
    )
    class Meta:
        ordering = ['position']
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
# Create your models here.
