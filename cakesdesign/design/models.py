from django.db import models
from django.urls import reverse


class Products(models.Model):
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание товара")
    price = models.FloatField(verbose_name="Стоимость")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d", verbose_name="Фото")
    available = models.BooleanField(default="True", verbose_name="Наличие")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Категория")
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['id']


class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = 'Категории товаров'
        ordering = ['id']


class Recipes(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d", verbose_name="Фото")
    recipe = models.TextField(blank=True, verbose_name="Рецепт")
    catdessert = models.ForeignKey('CategoryDessert', on_delete=models.PROTECT, verbose_name="Категория_Десерта")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
       return reverse('constructor', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['id']


class Ingredients(models.Model):
    title = models.CharField(max_length=255, verbose_name="Ингредиент")
    manufacturer = models.CharField(max_length=100, blank=False, default=None, verbose_name="Производитель")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
       return reverse('product', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['title']


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.PROTECT, verbose_name="Рецепт")
    ingredient = models.ForeignKey(Ingredients, on_delete=models.PROTECT, verbose_name="Ингредиент")
    count = models.FloatField(verbose_name="Масса ингредиента")
    measure = models.CharField(max_length=255, verbose_name="Единица измерения")

    def __str__(self):
        return self.measure

    def get_absolute_url(self):
       return reverse('constructor', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Рецепты-Ингредиенты'
        verbose_name_plural = 'Рецепты-Ингредиенты'
        ordering = ['id']


class CategoryDessert(models.Model):
    title = models.CharField(max_length=100, db_index=True, verbose_name="Тип_Десерта")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catdessert', kwargs={'catdessert_slug': self.slug})

    class Meta:
        verbose_name = "Тип десерта"
        verbose_name_plural = 'Типы десертов'
        ordering = ['id']
