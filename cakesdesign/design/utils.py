from django.db.models import *
from django.core.cache import cache
from .models import *

class DataMixin:
    #paginate_by = 30

    def get_context(self, **kwargs):
        context = kwargs
        cats = Category.objects.all()
        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context