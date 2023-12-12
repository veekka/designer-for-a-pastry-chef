from io import BytesIO
from textwrap import TextWrapper

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4

import json
import ast
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
            koef = (form_params * form_params) / 100
            cake_recipe = request.POST.get("cake_recipe", "Undefined")
            r = Recipes.objects.get(pk=cake_recipe)
            recipe = r.recipe
            photo = r.photo
            d = RecipesIngredients.objects.values('count', 'measure', 'ingredient_id').filter(recipe_id=cake_recipe)

            recipe_dict = {}

            for i in range(len(d)):
                recipe_dict[Ingredients.objects.get(pk=d[i]['ingredient_id'])] = str(math.ceil(d[i]['count']*koef)) +\
                                                                                 " " + d[i]['measure']

            context = {
                "title": r.title,
                "recipe_dict": recipe_dict,
                "recipe": recipe,
                "photo": photo,
                "form_params": form_params,
            }

            #вывод в файл для генерации пдф
            d_context = {}
            d_ingred = {}

            for k, v in context["recipe_dict"].items():
                d_ingred[str(k)] = str(v)

            for k, v in context.items():
                d_context[k] = str(v)

            d_context["d_ingred"] = d_ingred

            context_json = json.dumps(d_context)
            with open("context.json", "w") as file:
                file.write(context_json)

            return render(request, 'design/cakerecipe.html', context=context)
    else:
        form = BycakerecipeForm()
    return render(request, 'design/bycakerecipe.html', {"title": "Выбор торта", "form": form})


def constructor(request):
    if request.method == 'POST':
        form = CompoundRecipesForm(request.POST)
        if form.is_valid():
            form_params = float(request.POST.get("form_params", 10))
            koef = (form_params * form_params) / 100
            crust_choice = request.POST.get("crust_choice", "Undefined")
            filling_choice = request.POST.get("filling_choice", "Undefined")
            cream_choice_in = request.POST.get("cream_choice_in", "Undefined")
            cream_choice_out = request.POST.get("cream_choice_out", "Undefined")

            res_tb = Recipes.objects.all()
            res_ingred_tb = RecipesIngredients.objects.all()
            ingred_tb = Ingredients.objects.all()

            title_crust, photo_crust, recipe_crust, ingred_dict_crust = get_item_details(crust_choice, res_tb,
                                                                                res_ingred_tb, ingred_tb, koef)
            title_filling, photo_filling, recipe_filling, ingred_dict_filling = get_item_details(filling_choice,
                                                                                res_tb, res_ingred_tb, ingred_tb, koef)
            title_cream_in, photo_cream_in, recipe_cream_in, ingred_dict_cream_in = get_item_details(cream_choice_in,
                                                                                res_tb, res_ingred_tb, ingred_tb, koef)
            title_cream_out, photo_cream_out, recipe_cream_out, ingred_dict_cream_out = get_item_details(
                                                            cream_choice_out, res_tb, res_ingred_tb, ingred_tb, koef)

            all_ingred_dict = {}
            all_ingred_keys = list(set(list(ingred_dict_crust.keys()) + list(ingred_dict_cream_in.keys())+
                                       list(ingred_dict_filling.keys()) + list(ingred_dict_cream_out.keys())))
            for i in range(len(all_ingred_keys)):
                all_ingred_dict[all_ingred_keys[i]] = str(
                int(ingred_dict_crust.get(all_ingred_keys[i], "0 г").split()[0])+
                int(ingred_dict_filling.get(all_ingred_keys[i], "0 г").split()[0])+
                int(ingred_dict_cream_in.get(all_ingred_keys[i], "0 г").split()[0]) +
                int(ingred_dict_cream_out.get(all_ingred_keys[i], "0 г").split()[0]))+\
                ingred_dict_crust.get(all_ingred_keys[i], "0 г").split()[1]

            context = {
                "title": "Составной рецепт",
                "ingred_dict_crust": ingred_dict_crust,
                "title_crust": title_crust,
                "recipe_crust": recipe_crust,
                "photo_crust": photo_crust,
                "ingred_dict_filling": ingred_dict_filling,
                "title_filling": title_filling,
                "recipe_filling": recipe_filling,
                "photo_filling": photo_filling,
                "ingred_dict_cream_in": ingred_dict_cream_in,
                "title_cream_in": title_cream_in,
                "recipe_cream_in": recipe_cream_in,
                "photo_cream_in": photo_cream_in,
                "ingred_dict_cream_out": ingred_dict_cream_out,
                "title_cream_out": title_cream_out,
                "recipe_cream_out": recipe_cream_out,
                "photo_cream_out": photo_cream_out,
                "all_ingred_dict": all_ingred_dict,
                "form_params": form_params,
            }

            d_context = {}
            d_ingred = {}
            d_all_ingred = {}
            for part in ["_crust", "_filling", "_cream_in", "_cream_out"]:
                d = {}
                for k, v in context["ingred_dict"+part].items():
                    d[str(k)] = str(v)
                d_ingred[part] = d

            for k, v in context["all_ingred_dict"].items():
                d_all_ingred[str(k)] = str(v)

            for k, v in context.items():
                d_context[k] = str(v)

            d_context["d_ingred"] = d_ingred
            d_context["d_all_ingred"] = d_all_ingred

            context_json = json.dumps(d_context)
            with open("context.json", "w") as file:
                file.write(context_json)

            return render(request, 'design/compound_recipe.html', context=context)
    else:
        form = CompoundRecipesForm()
    return render(request, 'design/constructor.html', {"title": "Части торта", "form": form})


def get_item_details(choice, item, res_ingred_tb, ingred_tb, koef):
    r = item.get(pk=choice)
    title = r.title
    photo = r.photo
    recipe = r.recipe
    d_item = res_ingred_tb.values('count', 'measure', 'ingredient_id').filter(recipe_id=choice)

    dict_ingred_item = {}
    for i in range(len(d_item)):
        dict_ingred_item[ingred_tb.get(pk=d_item[i]['ingredient_id'])] = str(
            math.ceil(d_item[i]['count'] * koef)) + " " + d_item[i]['measure']

    return (title, photo, recipe, dict_ingred_item)

def delivery(request):
    return render(request, 'design/delivery.html')


def contact(request):
    return render(request, 'design/contact.html')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')



def generate_recipe_pdf(request):
    with open("context.json", "r") as file:
        context_json = file.read()
    context = json.loads(context_json)

    response = HttpResponse(content_type='application/pdf')
    file_name = context["title"]
    response['Content-Disposition'] = f'inline; filename="{file_name}.pdf"'
    width, height = A4
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    path_image_background = "C:/Users/Zaits/PycharmProjects/designer-for-a-pastry-chef/cakesdesign/media/photos/2023/11/08/odnotonnie-oboi.jpg"
    c.drawImage(path_image_background, 0, 0, width=width, height=height)


    faceName = cyrillic()

    size_title = 35
    size_chapter = 20
    size_text = 9

    #ОФОРМЛЯЕМ КАРТИНКУ
    path_image = "C:/Users/Zaits/PycharmProjects/designer-for-a-pastry-chef/cakesdesign/media/" + context["photo"]
    c.drawImage(path_image, 30, 620, width=250, height=200)
    #ОФОРМЛЯЕМ ЗАГОЛОВОК
    text = context["title"].split("\n")
    y_title = draw_wrap_text(c, width=15, text=text, x_begin=310, y_begin=750, faceName=faceName,
              size=size_title, interval=40,  path_image_background=path_image_background, r=0.9, g=0.5, b=0.4)


    # ОФОРМЛЯЕМ ИНГРЕДИЕНТЫ
    c.setFillColorRGB(0.9, 0.5, 0.4)
    c.setFont(faceName + '1251', size_chapter)
    c.drawString(50, 550, "ИНГРЕДИЕНТЫ:")
    c.setFont(faceName + '1251', 10)
    c.drawString(50, 535, f"На форму {context['form_params']} см")
    l = []
    for k, v in context["d_ingred"].items():
        l.append(f"□  {v} — {k}")

    y_ingred = draw_wrap_text(c, width=40, text=l, x_begin=50, y_begin=515, faceName=faceName,
              size=size_text, interval=15,  path_image_background=path_image_background, r=0, g=0, b=0)

    #СДЕЛАЕМ ПРЯМОУГОНИК
    c.setStrokeColorRGB(0.9, 0.5, 0.4)
    c.setLineWidth(4)
    c.rect(30, y_ingred-20, 250, (550-y_ingred+60), stroke=1, fill=0)

    #ОФОРМЛЯЕМ КАК ГОТОВИТЬ
    c.setFillColorRGB(0.9, 0.5, 0.4)
    c.setFont(faceName + '1251', size_chapter)
    if y_title >= 550:
        y_cook = 550
    else:
        y_cook = y_title-50
    c.drawString(300, y_cook, "КАК ГОТОВИТЬ:")
    text = context["recipe"].split("\n")
    draw_wrap_text(c, width=55, text=text, x_begin=300, y_begin=y_cook-30, faceName=faceName, size=size_text,
              interval=12, path_image_background=path_image_background, r=0, g=0, b=0)

    c.setTitle(f'{file_name}')
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def generate_compound_recipe_pdf(request):
    with open("context.json", "r") as file:
        context_json = file.read()
    context = json.loads(context_json)

    response = HttpResponse(content_type='application/pdf')
    file_name = "Рецепт составного торта"
    response['Content-Disposition'] = f'inline; filename="{file_name}.pdf"'
    width, height = A4
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    faceName = cyrillic()

    size_title = 35
    size_chapter = 20
    size_text = 9

    x_img = 30
    x_left = 50
    y_left = 620
    x_right = 300
    y_right = 750
    # ФОН
    path_image_background = "C:/Users/Zaits/PycharmProjects/designer-for-a-pastry-chef/cakesdesign/media/photos/2023/11/08/odnotonnie-oboi.jpg"

    for part in ["_crust", "_filling", "_cream_in", "_cream_out"]:

        c.drawImage(path_image_background, 0, 0, width=width, height=height)

        # ОФОРМЛЯЕМ КАРТИНКУ
        path_image = "C:/Users/Zaits/PycharmProjects/designer-for-a-pastry-chef/cakesdesign/media/" + context["photo"+part]
        c.drawImage(path_image, x_img, y_left, width=250, height=200)
        # ОФОРМЛЯЕМ ЗАГОЛОВОК
        text = context["title"+part].split("\n")
        y_title = draw_wrap_text(c, width=13, text=text, x_begin=x_right, y_begin=y_right, faceName=faceName,
                                 size=size_title, interval=40, path_image_background=path_image_background, r=0.9,
                                 g=0.5, b=0.4)
        # ОФОРМЛЯЕМ ИНГРЕДИЕНТЫ
        c.setFillColorRGB(0.9, 0.5, 0.4)
        c.setFont(faceName + '1251', size_chapter)
        c.drawString(x_left, y_left-70, "ИНГРЕДИЕНТЫ:")
        c.setFont(faceName + '1251', 10)
        c.drawString(x_left, y_left-85, f"На форму {context['form_params']} см")
        l = []
        for k, v in context["d_ingred"][part].items():
            l.append(f"□  {v} — {k}")

        y_ingred = draw_wrap_text(c, width=40, text=l, x_begin=x_left, y_begin=y_left-105, faceName=faceName,
                                  size=size_text, interval=15, path_image_background=path_image_background, r=0, g=0,
                                  b=0)

        # СДЕЛАЕМ ПРЯМОУГОНИК
        c.setStrokeColorRGB(0.9, 0.5, 0.4)
        c.setLineWidth(4)
        c.rect(x_img, y_ingred - 20, 250, (y_left-70 - y_ingred + 60), stroke=1, fill=0)
        # ОФОРМЛЯЕМ КАК ГОТОВИТЬ
        c.setFillColorRGB(0.9, 0.5, 0.4)
        c.setFont(faceName + '1251', size_chapter)
        if y_title >= y_left-70:
            y_cook = y_left-70
        else:
            y_cook = y_title - 50
        c.drawString(x_right, y_cook, "КАК ГОТОВИТЬ:")
        text = context["recipe"+part].split("\n")
        draw_wrap_text(c, width=55, text=text, x_begin=x_right, y_begin=y_cook - 30, faceName=faceName, size=size_text,
                  interval=12, path_image_background=path_image_background, r=0, g=0, b=0)

        c.showPage()
        y_left = 620
        y_right = 750

    # ОФОРМЛЯЕМ ВСЕ ИНГРЕДИЕНТЫ
    c.drawImage(path_image_background, 0, 0, width=width, height=height)
    c.setFillColorRGB(0.9, 0.5, 0.4)
    c.setFont(faceName + '1251', size_chapter)
    c.drawString(x_left, 800, "ВСЕ ИНГРЕДИЕНТЫ:")
    c.setFont(faceName + '1251', 10)
    c.drawString(x_left, 785, f"На форму {context['form_params']} см")
    l = []
    for k, v in context["d_all_ingred"].items():
        l.append(f"□  {v} — {k}")

    draw_wrap_text(c, width=40, text=l, x_begin=x_left, y_begin=760, faceName=faceName,
                              size=size_text, interval=15, path_image_background=path_image_background, r=0, g=0,
                              b=0)
    c.showPage()
    c.setTitle(f'{file_name}')
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def draw_wrap_text(c, width, text, y_begin, faceName, size, interval, x_begin, path_image_background, r,g,b):
    wrapper = TextWrapper(width)
    wrapped_text = list()
    for line in text:
        wrapped_text += wrapper.wrap(line)

    text_object = c.beginText()
    text_object.setTextOrigin(x_begin, y_begin)
    text_object.setFont(faceName + '1251', size)
    text_object.setFillColorRGB(r, g, b)

    for line in wrapped_text:
        text_object.setFont(faceName + '1251', size)
        text_object.setLeading(interval)
        text_object.textLine(line)
        y_begin -= interval

        if y_begin <= interval:
            c.drawText(text_object)
            c.showPage()
            c.drawImage(path_image_background, 0, 0, width=600, height=850)
            text_object = c.beginText(x_begin, 800)
            y_begin = 800

    c.drawText(text_object)
    return y_begin

def cyrillic():

    fname = 'a010013l'

    faceName = 'URWGothicL-Book'
    cyrFace = pdfmetrics.EmbeddedType1Face(fname + '.afm', fname + '.pfb')
    cyrenc = pdfmetrics.Encoding('CP1251')
    cp1251 = (
        'afii10051', 'afii10052', 'quotesinglbase', 'afii10100', 'quotedblbase',
        'ellipsis', 'dagger', 'daggerdbl', 'Euro', 'perthousand', 'afii10058',
        'guilsinglleft', 'afii10059', 'afii10061', 'afii10060', 'afii10145',
        'afii10099', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright',
        'bullet', 'endash', 'emdash', 'tilde', 'trademark', 'afii10106',
        'guilsinglright', 'afii10107', 'afii10109', 'afii10108', 'afii10193',
        'space', 'afii10062', 'afii10110', 'afii10057', 'currency', 'afii10050',
        'brokenbar', 'section', 'afii10023', 'copyright', 'afii10053',
        'guillemotleft', 'logicalnot', 'hyphen', 'registered', 'afii10056',
        'degree', 'plusminus', 'afii10055', 'afii10103', 'afii10098', 'mu1',
        'paragraph', 'periodcentered', 'afii10071', 'afii61352', 'afii10101',
        'guillemotright', 'afii10105', 'afii10054', 'afii10102', 'afii10104',
        'afii10017', 'afii10018', 'afii10019', 'afii10020', 'afii10021',
        'afii10022', 'afii10024', 'afii10025', 'afii10026', 'afii10027',
        'afii10028', 'afii10029', 'afii10030', 'afii10031', 'afii10032',
        'afii10033', 'afii10034', 'afii10035', 'afii10036', 'afii10037',
        'afii10038', 'afii10039', 'afii10040', 'afii10041', 'afii10042',
        'afii10043', 'afii10044', 'afii10045', 'afii10046', 'afii10047',
        'afii10048', 'afii10049', 'afii10065', 'afii10066', 'afii10067',
        'afii10068', 'afii10069', 'afii10070', 'afii10072', 'afii10073',
        'afii10074', 'afii10075', 'afii10076', 'afii10077', 'afii10078',
        'afii10079', 'afii10080', 'afii10081', 'afii10082', 'afii10083',
        'afii10084', 'afii10085', 'afii10086', 'afii10087', 'afii10088',
        'afii10089', 'afii10090', 'afii10091', 'afii10092', 'afii10093',
        'afii10094', 'afii10095', 'afii10096', 'afii10097'
    )

    for i in range(128, 256):
        cyrenc[i] = cp1251[i - 128]

    pdfmetrics.registerEncoding(cyrenc)
    pdfmetrics.registerTypeFace(cyrFace)
    pdfmetrics.registerFont(pdfmetrics.Font(faceName + '1251', faceName, 'CP1251'))

    return faceName