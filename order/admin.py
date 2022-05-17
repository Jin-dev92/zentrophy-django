from django.contrib import admin

# Register your models here.
from order.models import Order, DocumentFile, Subside, IntegratedFeePlan, ExtraSubside

admin.site.register(Order)
admin.site.register(DocumentFile)
admin.site.register(Subside)
admin.site.register(ExtraSubside)
admin.site.register(IntegratedFeePlan)
