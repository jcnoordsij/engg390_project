# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.encoding import python_2_unicode_compatible
import datetime
from django.utils import timezone
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from djrichtextfield.models import RichTextField
import os

fs = FileSystemStorage()

# Create your models here.


@python_2_unicode_compatible   
class Foundry(models.Model):
    
    name = models.CharField(max_length=25, unique=True)
    
    def __str__(self):
        return self.name
        
        
@python_2_unicode_compatible
class Process(models.Model):

    name = models.CharField(max_length=25)
    foundry = models.ForeignKey(Foundry, on_delete=models.CASCADE, related_name='processes', null=True)
    
    def __str__(self):
        return self.name
    
@python_2_unicode_compatible
class Wafer(models.Model):
    
    name = models.CharField(max_length=25)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='wafers', null=True)
    
    def __str__(self):
        return self.name

@python_2_unicode_compatible 
class Testplan(models.Model):

    STATUSES = [
        ('backlog', 'backlog'),
        ('priority_1', 'priority 1'),
        ('priority_2', 'priority 2'),
        ('wip', 'work in progress'),
        ('done', 'done')
    ]
    
    s_parameters = models.BooleanField(default=False)
    pulsed_IV = models.BooleanField(default=False)
    load_pull = models.BooleanField(default=False)
    imax_droop = models.BooleanField(default=False)
    foundry = models.ForeignKey(Foundry, on_delete=models.CASCADE, null=True)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=True)
    wafers = models.ManyToManyField(Wafer, related_name='testplans')
    issue_date = models.DateTimeField('date issued')
    primary_contact = models.CharField(max_length=50, null=True)
    file = models.FileField(null=True, upload_to='documents/%Y/%m/', storage=fs)
    notes = RichTextField(null=True)
    status = models.CharField(max_length=25, choices=STATUSES, default='priority_1')
    archived = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        return reverse('testplans:testplan_detail', kwargs={'pk':str(self.pk)})
    
    def filename(self):
        if self.file is not None:
            return os.path.basename(self.file.name)
        else:
            raise Exception('Testplan instance''s file field value is null!')
            
    def __str__(self):
        return str(self.process)
