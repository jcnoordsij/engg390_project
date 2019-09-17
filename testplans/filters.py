from .models import Testplan
import django_filters
from django import forms
from django.db import models
from django.db.models import Q
from django_filters.widgets import RangeWidget


class TestplanFilterset(django_filters.FilterSet):
    
    date_range = django_filters.DateFromToRangeFilter(name='issue_date',widget=RangeWidget(attrs={'type': 'date'}))
    
    search = django_filters.CharFilter(method='filter_by_multiple_fields')
    
    class Meta:
        model = Testplan
        fields = {
            'archived':['exact'],
            'status':['exact'],
            'process':['exact'],
            'foundry':['exact'],
        }
        filter_overrides = {
            models.BooleanField: {
                'filter_class': django_filters.BooleanFilter,
                'extra': lambda f: {
                    'widget': forms.CheckboxInput,
                },
            },
        }
     
    def filter_by_multiple_fields(self, queryset, name, value):
        return queryset.filter(
            Q(foundry__name__icontains=value) | Q(process__name__icontains=value) | Q(notes__icontains=value) | Q(primary_contact__icontains=value) | Q(wafers__name__icontains=value) 
        )
    
    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        data.setdefault('archived', 'false')
        data.setdefault('order', '-issue_date')
        super(TestplanFilterset, self).__init__(data, *args, **kwargs)