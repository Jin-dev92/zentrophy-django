from django.contrib import admin

# Register your models here.
from history.models import Refund, AfterService, Warranty, Cart, PrevEstimate

admin.site.register(Refund)
admin.site.register(AfterService)
admin.site.register(Warranty)
admin.site.register(Cart)
admin.site.register(PrevEstimate)
