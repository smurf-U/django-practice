from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from .models import *

admin.site.site_header = "Sales Admin"
admin.site.site_title = "Sales Admin Portal"
admin.site.index_title = "Welcome to Sales Admin Portal"

admin.site.register(Category)
def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse('admin:{}_{}_change'.format(
        app_label, model_name
    ), args=(obj.pk,))
def admin_link(attr, short_description, empty_description="-"):
    """Decorator used for rendering a link to a related model in
    the admin detail page.
    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.
    The wrapped method receives the related object and should
    return the link text.
    Usage:
        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """
    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html(
                '<a href="{}">{}</a>',
                url,
                func(self, related_obj)
            )
        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func
    return wrap

@admin.register(AttributeCategory)
class AttributeCategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'description']


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    # fields = ['name', 'description']
    list_display = ['attribute', 'name', 'html_color', 'is_custom']


class AttributeValueTabInline(admin.TabularInline):
    model = AttributeValue
    extra = 0


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    # fields = ['name', 'description']
    list_display = ['name', 'type', 'category']
    inlines = [AttributeValueTabInline]


class ProductAttributeValueLineTabInline(admin.TabularInline):
    model = AttributeValueLine
    extra = 0


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "Category: {}".format(obj.name)


@admin.register(Template)
class ProductTemplateAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'categ', 'price']
    inlines = [ProductAttributeValueLineTabInline]
    readonly_fields = ['headshot_image']
    raw_id_fields = ["categ"]
    list_select_related = (
        'categ',
    )

    @admin_link('categ', 'Category')
    def category_link(self, categ):
        return categ

    def headshot_image(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
            )
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'categ':
            return CategoryChoiceField(queryset=Category.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
