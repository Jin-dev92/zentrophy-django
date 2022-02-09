from django.contrib import admin

# Register your models here.
from placement.models import Placement, PlacementImage

admin.site.register(Placement)
admin.site.register(PlacementImage)