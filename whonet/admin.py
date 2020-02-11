from django.contrib import admin
from django.contrib.auth.models import User,Permission

# Register your models here.

from .models import RawFileName, RawOrigin, RawLocation, RawMicrobiology, RawSpecimen, RawAntidisk, RawAntimic


admin.site.register(RawFileName)
admin.site.register(RawOrigin)
admin.site.register(RawLocation)
admin.site.register(RawMicrobiology)
admin.site.register(RawSpecimen)
admin.site.register(RawAntidisk)
admin.site.register(RawAntimic)
admin.site.register(Permission)
