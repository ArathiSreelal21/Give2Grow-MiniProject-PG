from django.contrib import admin
from .models import Donation, Orphanage, EducationalInstitution,UserRegistration,PaymentHistory,Request
# Register your models here.

admin.site.register(UserRegistration)
admin.site.register(Donation)
admin.site.register(EducationalInstitution)
admin.site.register(Orphanage)
admin.site.register(PaymentHistory)
admin.site.register(Request)