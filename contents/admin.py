from django.contrib import admin
from .models import Donor, Donation, AdminProfile,DonationCategory

admin.site.register(Donor)
admin.site.register(Donation)
admin.site.register(AdminProfile)
admin.site.register(DonationCategory)