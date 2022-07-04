from django.contrib import admin

# Register your models here.
from order.models import Order, DocumentFile, Subside, ExtraSubside, CustomerInfo, OrderLocationInfo, \
    OrderedProductOptions, OrderedVehicleColor, Subscriptions, ProductDeliveryInfo, Payment

admin.site.register(Order)
admin.site.register(DocumentFile)
admin.site.register(Subside)
admin.site.register(ExtraSubside)
admin.site.register(CustomerInfo)
admin.site.register(OrderLocationInfo)
admin.site.register(OrderedProductOptions)
admin.site.register(OrderedVehicleColor)
admin.site.register(Subscriptions)
admin.site.register(ProductDeliveryInfo)
admin.site.register(Payment)
