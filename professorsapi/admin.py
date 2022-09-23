from django.contrib import admin
from coreapp.models import *
from accounts.models import *
# Register your models here.
admin.site.register(Post)
admin.site.register(Appointment)
admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(ProfessorGroup)
admin.site.register(Expertise)
admin.site.register(Location)
admin.site.register(User)

