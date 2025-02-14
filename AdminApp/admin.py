from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(MainCategoryModel)
admin.site.register(SubCategoryModel)
admin.site.register(StateModel)
admin.site.register(DistrictsModel)
admin.site.register(DonationCategoryModel)
admin.site.register(Poster)
