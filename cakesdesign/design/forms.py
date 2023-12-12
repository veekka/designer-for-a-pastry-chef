from django import forms
from .models import *


class CompoundRecipesForm(forms.Form):
    form_params = forms.FloatField(max_value=100, min_value=10, label='Размер формы в см')
    crust_choice = forms.ModelChoiceField(queryset=Recipes.objects.filter(catdessert__title__contains="Корж"),
                                       label='Корж', empty_label="Корж не выбран")
    filling_choice = forms.ModelChoiceField(queryset=Recipes.objects.filter(catdessert__title__contains="Начинка"),
                                          label='Начинка', empty_label="Начинка не выбрана")
    cream_choice_in = forms.ModelChoiceField(queryset=Recipes.objects.filter(catdessert__title__contains="Крем для коржей"),
                                       label='Крем для коржей', empty_label="Крем не выбран")
    cream_choice_out = forms.ModelChoiceField(queryset=Recipes.objects.filter(
        catdessert__title__contains="Крем для выравнивания"), label='Крем для выравнивания', empty_label="Крем не выбран")



class BycakerecipeForm(forms.Form):
    form_params = forms.FloatField(label='Размер формы в см')
    cake_recipe = forms.ModelChoiceField(queryset=Recipes.objects.filter(catdessert__title__contains="Торт"),
                                         label='Рецепт', empty_label="Торт не выбран")
