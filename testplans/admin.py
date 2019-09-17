# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Testplan, Wafer, Foundry, Process
from .forms import TestplanForm

# Register your models here.

class TestplanAdmin(admin.ModelAdmin):
    form = TestplanForm
    fieldsets = [
        (None, {'fields': ['primary_contact','foundry', 'wafers', 'process','status','notes','file']}),
        ('Measurements', {'fields': ['s_parameters', 'pulsed_IV', 'load_pull', 'imax_droop']}),
        ('Date information', {'fields': ['issue_date']}),
    ]
    list_display = ('process', 'issue_date')
    list_filter = ['issue_date']
    search_fields = ['title','foundry__name','wafers__name','process__name','issue_date']
    
class FoundryAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    list_display = ('name')
    
class ProcessAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None, {'fields': ['name', 'foundry']}),
    ]
    list_display = ('name')
    list_filter = ['foundry']
    search_fields = ['name']
    
class WaferAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None, {'fields': ['name', 'foundry', 'process']}),
    ]
    
    list_display = ('name')
    list_filter = ['foundry']
    search_fields = ['name']

    
admin.site.register(Testplan, TestplanAdmin)
admin.site.register(Foundry)
admin.site.register(Process)
admin.site.register(Wafer)