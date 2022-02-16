from django.contrib import admin

# Register your models here.
from history.models import Refund, AfterService, BatteryExchange, Warranty

admin.site.register(Refund)
admin.site.register(AfterService)
admin.site.register(BatteryExchange)
admin.site.register(Warranty)
