from django import template
from resources.models import Product

register = template.Library()

@register.filter
def get_product(product_id):
    try:
        product_obj = Product.objects.get(pk__exact=product_id)
        return product_obj.service_name
    except:
        return ""
