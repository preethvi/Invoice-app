from django.contrib import admin
from .models import Company, Client

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    search_fields = ('name', 'contact')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    search_fields = ('name', 'contact')

