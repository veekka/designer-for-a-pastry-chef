from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
import math
from design.forms import *
from design.models import *
from design.utils import DataMixin
from cart.forms import CartAddProductForm


class DesignHome(DataMixin, ListView):
    model = Products
    template_name = 'design/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_context(title="Главная страница")
        return {**context, **c_def}


class ShowCatalog(DataMixin, ListView):
    model = Products
    template_name = 'design/catalog.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        cart_product_form = CartAddProductForm()
        context = super().get_context_data(**kwargs)
        c_def = self.get_context(title="Каталог", cart_product_form=cart_product_form)
        return dict(list(context.items()) + list(c_def.items()))


class ShowCategory(DataMixin, ListView):
    model = Products
    template_name = 'design/category.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        cart_product_form = CartAddProductForm()
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        prods = Products.objects.filter(cat_id=c.pk)
        p_def = {'prods': prods}
        c_def = self.get_context(title='Категория: ' + str(c.title), cat_selected=c.pk, cart_product_form=cart_product_form)
        return dict(list(context.items()) + list(c_def.items()) + list(p_def.items()))


class ShowProduct(DataMixin, DetailView):
    model = Products
    template_name = 'design/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_context_data(self, *, object_list=None, **kwargs):
        cart_product_form = CartAddProductForm()
        context = super().get_context_data(**kwargs)
        c_def = self.get_context(title="Продукт", cart_product_form=cart_product_form)
        return {**context, **c_def}


def makechoice(request):
    return render(request, 'design/makechoice.html')

def bycakerecipe(request):
    if request.method == 'POST':
        form = BycakerecipeForm(request.POST)
        if form.is_valid():
            form_params = float(request.POST.get("form_params", 10))
            cake_recipe = request.POST.get("cake_recipe", "Undefined")
            r = Recipes.objects.get(pk=cake_recipe)
            recipe = r.recipe
            photo = r.photo
            d = RecipesIngredients.objects.values('count', 'measure', 'ingredient_id').filter(recipe_id=cake_recipe)
            if form_params > 10:
                koef = int((form_params*form_params) / 100)
            else:
                koef = 1
            recipe_dict = {}
            for i in range(len(d)):
                recipe_dict[Ingredients.objects.get(pk=d[i]['ingredient_id'])] = str(math.ceil(d[i]['count']*koef)) +\
                                                                                 " " + d[i]['measure']

            context = {
                "title": "Рецепт",
                "recipe_dict": recipe_dict,
                "recipe": recipe,
                "photo": photo,
                "form_params": form_params,
            }
            return render(request, 'design/cakerecipe.html', context=context)
    else:
        form = BycakerecipeForm()
    return render(request, 'design/bycakerecipe.html', {"title": "Выбор торта", "form": form})


def constructor(request):
    if request.method == 'POST':
        form = CompoundRecipesForm(request.POST)
        if form.is_valid():
            form_params = float(request.POST.get("form_params", 10))
            crust_choice = request.POST.get("crust_choice", "Undefined")
            cream_choice_in = request.POST.get("cream_choice_in", "Undefined")
            cream_choice_out = request.POST.get("cream_choice_out", "Undefined")

            if form_params > 10:
                koef = int((form_params*form_params) / 100)
            else:
                koef = 1

            res_tb = Recipes.objects.all()
            res_ingred_tb = RecipesIngredients.objects.all()
            ingred_tb = Ingredients.objects.all()

            r_crust = res_tb.get(pk=crust_choice)
            recipe_crust = r_crust.recipe
            photo_crust = r_crust.photo
            d_crust = res_ingred_tb.values('count', 'measure', 'ingredient_id').filter(recipe_id=crust_choice)

            r_cream_in = res_tb.get(pk=cream_choice_in)
            recipe_cream_in = r_cream_in.recipe
            photo_cream_in = r_cream_in.photo
            d_cream_in = res_ingred_tb.values('count', 'measure', 'ingredient_id').filter(
                recipe_id=cream_choice_in)

            r_cream_out = res_tb.get(pk=cream_choice_out)
            recipe_cream_out = r_cream_out.recipe
            photo_cream_out = r_cream_out.photo
            d_cream_out = res_ingred_tb.values('count', 'measure', 'ingredient_id').filter(
                recipe_id=cream_choice_out)

            ingred_dict_crust = {}
            for i in range(len(d_crust)):
                ingred_dict_crust[ingred_tb.get(pk=d_crust[i]['ingredient_id'])] = str(
                    math.ceil(d_crust[i]['count']*koef)) + " " + d_crust[i]['measure']
            ingred_dict_cream_in = {}
            for i in range(len(d_cream_in)):
                ingred_dict_cream_in[ingred_tb.get(pk=d_cream_in[i]['ingredient_id'])] = str(
                    math.ceil(d_cream_in[i]['count'] * koef)) + " " + d_cream_in[i]['measure']

            ingred_dict_cream_out = {}
            for i in range(len(d_cream_out)):
                ingred_dict_cream_out[ingred_tb.get(pk=d_cream_out[i]['ingredient_id'])] = str(
                    math.ceil(d_cream_out[i]['count'] * koef)) + " " + d_cream_out[i]['measure']

            all_ingred_dict = {}
            all_ingred_keys = list(set(list(ingred_dict_crust.keys()) + list(ingred_dict_cream_in.keys())+
                                       list(ingred_dict_cream_out.keys())))
            for i in range(len(all_ingred_keys)):
                all_ingred_dict[all_ingred_keys[i]] = str(
                int(ingred_dict_crust.get(all_ingred_keys[i], "0 г").split()[0])+
                int(ingred_dict_cream_in.get(all_ingred_keys[i], "0 г").split()[0])+
                int(ingred_dict_cream_out.get(all_ingred_keys[i], "0 г").split()[0]))+\
                ingred_dict_crust.get(all_ingred_keys[i], "0 г").split()[1]

            context = {
                "title": "Составной рецепт",
                "ingred_dict_crust": ingred_dict_crust,
                "recipe_crust": recipe_crust,
                "photo_crust": photo_crust,
                "ingred_dict_cream_in": ingred_dict_cream_in,
                "recipe_cream_in": recipe_cream_in,
                "photo_cream_in": photo_cream_in,
                "ingred_dict_cream_out": ingred_dict_cream_out,
                "recipe_cream_out": recipe_cream_out,
                "photo_cream_out": photo_cream_out,
                "all_ingred_dict": all_ingred_dict,
                "form_params": form_params,
            }
            return render(request, 'design/compound_recipe.html', context=context)
    else:
        form = CompoundRecipesForm()
    return render(request, 'design/constructor.html', {"title": "Части торта", "form": form})



def delivery(request):
    return render(request, 'design/delivery.html')


def contact(request):
    return render(request, 'design/contact.html')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')