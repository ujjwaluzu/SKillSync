from django.contrib import admin

# Register your models here.
from .models import Project, Bid

admin.site.register(Project)
admin.site.register(Bid)