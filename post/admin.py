from django.contrib import admin

from post.models import FAQ, FAQCategory, Notice

admin.site.register(FAQ)
admin.site.register(FAQCategory)
admin.site.register(Notice)
