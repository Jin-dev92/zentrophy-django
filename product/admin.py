from django.contrib import admin

# Register your models here.
from product.models import Product, ProductImage, ProductDisplayLine, ProductOptions

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductDisplayLine)
admin.site.register(ProductOptions)
