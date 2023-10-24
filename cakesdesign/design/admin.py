from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('cat', 'title', 'photo', 'get_html_photo', 'available', 'time_create')
    search_fields = ('title', 'cat')
    list_filter = ('price', 'time_create')
    prepopulated_fields = {"slug": ("title",)}
    fields = ('cat', 'title', 'slug', 'description', 'price', 'photo', 'get_html_photo', 'available', 'time_create', 'time_update')
    readonly_fields = ('time_create', 'time_update', 'get_html_photo')
    save_on_top = True

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=50>")

    get_html_photo.short_description = "Миниатюра"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('title', 'photo', 'get_html_photo', 'recipe')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    fields = ('catdessert', 'title', 'slug', 'photo', 'get_html_photo', 'recipe')
    readonly_fields = ('get_html_photo',)
    save_on_top = True

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=50>")

    get_html_photo.short_description = "Миниатюра"


class CategoryDessertAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}


class IngredientsAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    fields = ('title', 'manufacturer')


class RecipesIngredientsAdmin(admin.ModelAdmin):
    fields = ('recipe', 'ingredient', 'count', 'measure')


admin.site.register(Products, ProductsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipesIngredients, RecipesIngredientsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryDessert, CategoryDessertAdmin)
#
# #admin.site.site_title = "Админ-панель сайта о женщинах"
# #admin.site.site_header = "Админ-панель сайта о женщинах 2"