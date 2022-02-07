from django.contrib import admin

# Register your models here.
from order.models import Order, NecessaryDocumentFile, Subside, ExtraSubside

admin.site.register(Order)
admin.site.register(NecessaryDocumentFile)
admin.site.register(ExtraSubside)
