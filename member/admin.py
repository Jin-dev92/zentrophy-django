from django.contrib import admin

# Register your models here.
from member.models import Member, MemberOwnedVehicles

admin.site.register(Member)
admin.site.register(MemberOwnedVehicles)
