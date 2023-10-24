from django.urls import path

from .views import *

urlpatterns = [
    path('', DesignHome.as_view(), name='home'),
    path('catalog/', ShowCatalog.as_view(), name='catalog'),
    path('product/<slug:product_slug>/', ShowProduct.as_view(), name='product'),
    path('category/<slug:cat_slug>/', ShowCategory.as_view(), name='category'),
    path('makechoice/', makechoice, name='makechoice'),
    path('bycakerecipe/', bycakerecipe, name='bycakerecipe'),
    path('cakerecipe/', bycakerecipe, name='cakerecipe'),
    path('constructor/', constructor, name='constructor'),
    path('compound_recipe/', constructor, name='compound_recipe'),
    path('delivery/', delivery, name='delivery'),
    path('contact/', contact, name='contact'),
]
