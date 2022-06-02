from django.contrib import admin

# Register your models here.
from member.models import User, MemberOwnedVehicles, RemoteToken, PaymentMethod, Card

admin.site.register(User)
admin.site.register(MemberOwnedVehicles)
admin.site.register(RemoteToken)
admin.site.register(PaymentMethod)
admin.site.register(Card)
