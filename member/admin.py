from django.contrib import admin

# Register your models here.
from member.models import User, RemoteToken, PaymentMethod, Card, OwnedVehicle

admin.site.register(User)
admin.site.register(RemoteToken)
admin.site.register(PaymentMethod)
admin.site.register(Card)
admin.site.register(OwnedVehicle)
