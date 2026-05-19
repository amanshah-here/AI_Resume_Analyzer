from django.contrib import admin
from .models import Contact, ResumeHistory, Donation

admin.site.register(Donation)
admin.site.register(Contact)
admin.site.register(ResumeHistory)