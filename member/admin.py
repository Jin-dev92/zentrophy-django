from django.contrib import admin

# Register your models here.
from member.models import User, MemberOwnedVehicles

admin.site.register(User)
admin.site.register(MemberOwnedVehicles)
