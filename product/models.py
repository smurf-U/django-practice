from django.core.exceptions import ValidationError
from django.db import models


class AttributeCategory(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Attribute(models.Model):
    name = models.CharField('Name', max_length=64)
    category = models.ForeignKey(AttributeCategory,
                                 verbose_name='Category',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True)
    type = models.CharField('Type', max_length=32, choices=[
        ('select', 'Select'),
        ('radio', 'Radio'),
        ('color', 'Color')
    ], default='select')

    create_variant = models.CharField(
        'Create Variants', max_length=32,
        choices=[
            ('no_variant', 'Never'),
            ('always', 'Always'),
            ('dynamic',
             'Only when the product is added to a sales order')
        ], default='always')

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class AttributeValue(models.Model):
    name = models.CharField('Value', max_length=64)
    attribute = models.ForeignKey(Attribute, related_name="value_ids",
                                  verbose_name='Attribute',
                                  on_delete=models.CASCADE)
    is_custom = models.BooleanField('Is custom value',
                                    help_text="Allow users to input custom "
                                              "values for this attribute value")
    html_color = models.CharField(max_length=64,
                                  blank=True,
                                  verbose_name='HTML Color Index',
                                  help_text="""Here you can set a
                specific HTML color index (e.g. #ff0000) to display the color if the
                attribute type is 'Color'.""")
    sequence = models.IntegerField('Sequence', default='0',
                                   help_text="Determine the display order")

    class Meta:
        app_label = 'product'
        indexes = [
            models.Index(fields=['attribute'], name='attribute_id_name_idx'),
            models.Index(fields=['sequence'], name='sequence_idx'),
        ]
        unique_together = [['name', 'attribute']]
        # error_messages = {
        #     'NON_FIELD_ERRORS': {
        #         'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
        #     }
        # }
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               related_name='child_ids', blank=True)
    image = models.ImageField(upload_to='product_category', blank=True)

    class Meta:
        app_label = 'product'
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return '%s / %s' % (self.parent.__str__(), self.name)
        else:
            return self.name

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        if not self.parent or self.parent.pk not in [child.pk for child in \
                self.child_ids.all()]:
            super(Category, self).save(*args, **kwargs)
        else:
            raise ValidationError("You cannot create recursive categories.")


def get_category():
    return Category.objects.all().order_by('id')[0] if Category.objects.all() \
        else None


class Template(models.Model):
    class Meta:
        app_label = 'product'
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = "Product"
        # ordering = ['id']
        # get_latest_by = 'name'

    name = models.CharField('Name', max_length=64)
    sku = models.CharField('SKU', max_length=64)
    image = models.ImageField('Image', upload_to='product_template/',
                              blank=True)
    description = models.TextField('Product Description', blank=True)
    description_purchase = models.TextField('Purchase Description',
                                            blank=True)
    description_sale = models.TextField(
        'Sale Description', blank=True,
        help_text="A description of the Product that you want to communicate "
                  "to your customers. This description will be copied to "
                  "every Sales Order, Delivery Order and Customer "
                  "Invoice/Credit Note")
    type = models.CharField('Type', max_length=32, choices=[
        ('product', 'Storable'),
        ('consu', 'Consumable'),
        ('service', 'Service')
    ], default='consu', help_text='A storable product is a  product for which '
                                  'you manage stock. The Inventory app has to '
                                  'be installed.\nA consumable product is a '
                                  'product for which stock is not managed.\n'
                                  'A service is a non-material product you '
                                  'provide.')
    rental = models.BooleanField('Can be Rent')
    categ = models.ForeignKey(Category, verbose_name='Category',
                              on_delete=models.SET_NULL,
                              default=get_category,
                              blank=True, null=True,
                              help_text="Select category for the current "
                                        "product")
    sale_ok = models.BooleanField('Can be Sold', default=True)
    active = models.BooleanField('Active', default=True)
    # currency_id = models.ForeignKey(Currency, on_delete=models.SET_NULL)
    price = models.FloatField('Price', default=1.0)


class AttributeValueLine(models.Model):
    product_tmpl = models.ForeignKey(Template,
                                     related_name='attribute_line_ids',
                                     verbose_name='Product Template',
                                     on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute,
                                  verbose_name="Attribute",
                                  on_delete=models.PROTECT)
    values = models.ManyToManyField(AttributeValue, verbose_name="Values")

    # product_template_value_ids = fields.Many2many(
    #     'product.template.attribute.value',
    #     string='Product Attribute Values',
    #     compute="_set_product_template_value_ids",
    #     store=False)

    # @api.constrains('value_ids', 'attribute_id')
    # def _check_valid_attribute(self):
    #     if any(
    #             not line.value_ids or line.value_ids > line.attribute_id.value_ids
    #             for line in self):
    #         raise ValidationError(
    #             _('You cannot use this attribute with the following value.'))
    #     return True

    class Meta:
        app_label = 'product'
        indexes = [
            models.Index(fields=['product_tmpl'], name='product_tmpl_idx'),
            models.Index(fields=['attribute'], name='attribute_idx'),
        ]
