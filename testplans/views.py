# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.conf import settings
import os
import mimetypes
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict, HttpResponseBadRequest, Http404
from .models import Testplan, Process, Foundry, Wafer
from django.shortcuts import render, get_object_or_404, render_to_response
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import simplejson as json
from .forms import FoundryForm, WaferForm, ProcessForm, TestplanForm
from django.forms import modelformset_factory
import logging
import datetime
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.template import RequestContext
from django.forms import modelformset_factory
from .utils import save_new_object, create_restyaboard_card
from .filters import TestplanFilterset
from rest_framework import viewsets
from .serializers import TestplanSerializer


class TestplanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows test plans to be viewed or edited.
    """
    queryset = Testplan.objects.all().order_by('-issue_date')
    serializer_class = TestplanSerializer


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print file_path
    if os.path.exists(file_path):
        file_type = mimetypes.guess_type(file_path, strict=False)
        if file_type[0] != None:
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=file_type[0])
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    raise Http404


def create_testplan(request):
    
    # Check for POST
    if request.method == 'POST':
        
        # New testplan submission
        if 'submit-testplan' in request.POST:
            form = TestplanForm(request.POST, request.FILES, prefix="testplan")
            if form.is_valid():
                new_tp = form.save(commit=False)
                new_tp.issue_date=timezone.now()
                new_tp.save()
                for wafer in form.cleaned_data['wafers']:
                    get_object_or_404(Testplan, pk=new_tp.id).wafers.add(get_object_or_404(Wafer, pk=wafer.pk))
                if form.cleaned_data['create_restya_card'] == True:
                    create_restyaboard_card(new_tp)
                return HttpResponseRedirect(reverse('testplans:testplan_list'))
            else:
                return HttpResponseBadRequest()
        else:
            
            # Save new foundry, process, or wafer
            response_code, new_obj = save_new_object(request)
            if response_code is not None:   
                return HttpResponse(status=response_code)
            
            # Go to form_submit view after new foundry, process, or wafer submission to reload testplan form with submitted values
            # We must return an HttpResponseRedirect to avoid form resubmission on reload
            return HttpResponseRedirect(reverse('testplans:form_submit', kwargs={'object':str.lower(new_obj.__class__.__name__),'pk':str(new_obj.pk)}))
    
    # Handle GET case
    else:
        testplan_form = TestplanForm(prefix="testplan")
        foundry_form = FoundryForm(prefix="foundry")
        process_form = ProcessForm(prefix="process")
        wafer_form = WaferForm(prefix="wafer")
        testplan_form.fields['process'].queryset = Process.objects.none();
        testplan_form.fields['wafers'].queryset = Wafer.objects.none();
        return render(request, 'testplans/create_testplan.html', {
            'testplan_form': testplan_form,
            'foundry_form': foundry_form,
            'process_form': process_form,
            'wafer_form': wafer_form,
        })
 
 
def form_submit(request, object, pk):
    testplan_form = TestplanForm(prefix="testplan")
    foundry_form = FoundryForm(prefix="foundry")
    process_form = ProcessForm(prefix="process")
    wafer_form = WaferForm(prefix="wafer")
    
    if object == 'process':
        foundry_pk = get_object_or_404(Process, pk=int(pk)).foundry.pk
        testplan_form.fields['foundry'].initial = foundry_pk
        testplan_form.fields['process'].queryset =  Process.objects.filter( foundry__id=foundry_pk )
        testplan_form.fields['process'].initial = int(pk)
        testplan_form.fields['wafers'].queryset = Wafer.objects.none()
    elif object == 'foundry':
        testplan_form.fields['foundry'].initial = int(pk)
        testplan_form.fields['process'].queryset = Process.objects.none();
        testplan_form.fields['wafers'].queryset = Wafer.objects.none();
    elif object == 'wafer':
        process_pk = get_object_or_404(Wafer, pk=int(pk)).process.pk
        foundry_pk = get_object_or_404(Process, pk=process_pk).foundry.pk
        testplan_form.fields['foundry'].initial = foundry_pk
        testplan_form.fields['process'].queryset = Process.objects.filter( foundry__id=foundry_pk )
        testplan_form.fields['process'].initial = process_pk
        testplan_form.fields['wafers'].queryset = Wafer.objects.filter( process__id=process_pk )
        
    return render(request, 'testplans/create_testplan.html', {
        'testplan_form': testplan_form,
        'foundry_form': foundry_form,
        'process_form': process_form,
        'wafer_form': wafer_form,
    })


def update_testplan(request, pk):
    
    tp = get_object_or_404(Testplan, pk=pk)

    # Check for POST
    if request.method == 'POST':
        
        # Update testplan
        if 'submit-testplan' in request.POST:
            form = TestplanForm(request.POST, request.FILES, prefix="testplan", instance=tp)
            if form.is_valid():
                form.save()
                tp.wafers.clear()
                for wafer in form.cleaned_data['wafers']:
                    tp.wafers.add(get_object_or_404(Wafer, pk=wafer.pk))
                return HttpResponseRedirect(reverse('testplans:testplan_detail', kwargs={'pk':str(pk)}))
            else:
                return HttpResponseBadRequest()
        else:
            
            # Save new foundry, process, or wafer
            response_code, new_obj = save_new_object(request)
            if response_code is not None:   
                return HttpResponse(status=response_code)
                
            # Reload current testplan if new foundry, process, or wafer is added
            # We must return an HttpResponseRedirect to avoid form resubmission on reload
            return HttpResponseRedirect(reverse('testplans:update_testplan', kwargs={'pk':pk}))
    
    # Handle GET case
    else:
        testplan_form = TestplanForm(prefix="testplan", instance=tp)
        foundry_form = FoundryForm(prefix="foundry")
        process_form = ProcessForm(prefix="process")
        wafer_form = WaferForm(prefix="wafer")
        testplan_form.fields['process'].queryset = Process.objects.filter( foundry__id=tp.foundry.pk )
        testplan_form.fields['wafers'].queryset = Wafer.objects.filter( process__id=tp.process.pk )

        return render(request, 'testplans/update_testplan.html', {
            'testplan_form': testplan_form,
            'foundry_form': foundry_form,
            'process_form': process_form,
            'wafer_form': wafer_form,
            'pk':pk,
        })


def archive_testplan(request, pk, to_archive):
    tp = get_object_or_404(Testplan, pk=pk)
    if to_archive == 'true':
        tp.archived = True
    else:
        tp.archived = False
    tp.save()
    return HttpResponseRedirect(reverse('testplans:testplan_list'))
    
    
class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # Get the queryset
        queryset = super(FilteredListView, self).get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(FilteredListView, self).get_context_data(**kwargs)
        # Pass the filterset to the template
        context['filterset'] = self.filterset
        return context


class TestplanListView(FilteredListView):
    model = Testplan
    context_object_name = 'testplans'
    paginate_by = 10
    filterset_class = TestplanFilterset


class TestplanDetailView(DetailView):
    model = Testplan
    

class TestplanUpdate(UpdateView):
    model = Testplan
    template_name_suffix = '_update_form'
    form_class = TestplanForm

    
class TestplanDelete(DeleteView):
    model = Testplan
    success_url = reverse_lazy('testplans:testplan_list')
    
    
def get_processes(request):
    try:
        foundry_id = request.GET['foundry_id']
    except KeyError:
        raise Http404
    foundry = get_object_or_404(Foundry, id=foundry_id)
    process_list = list( foundry.processes.all().values('id', 'name') )
    return JsonResponse({'process_list':process_list})
    
    
def get_wafers(request):
    try:
        process_id = request.GET['process_id']
    except KeyError:
        raise Http404
    process = get_object_or_404(Process, id=process_id)
    wafer_list = list( process.wafers.all().values('id', 'name') )
    return JsonResponse({'wafer_list':wafer_list})