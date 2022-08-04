from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Projects)
admin.site.register(ProjectsImages)
admin.site.register(BlendingWithCurrentImage)
admin.site.register(ZoomedImages)