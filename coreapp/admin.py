from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

# Register your models here.
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Appointment)
admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(Setting)
admin.site.register(Reference)
admin.site.register(Announce)
admin.site.register(Skill)
admin.site.register(ProfessorGroup)
admin.site.register(Expertise)
admin.site.register(Location)
admin.site.register(User)
admin.site.register(Circle)
admin.site.register(CircleType)