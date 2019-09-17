from django import forms
from .models import Testplan, Foundry, Process, Wafer
from django_select2.forms import Select2MultipleWidget, Select2Widget

class TestplanForm(forms.ModelForm):
    create_restya_card = forms.BooleanField(required=False)

    class Meta:
        model = Testplan
        fields = ('primary_contact','foundry','process','s_parameters','pulsed_IV','load_pull','imax_droop','file','notes','wafers','status')
        widgets = {
            'foundry': Select2Widget(),
            'process': Select2Widget(),
            'wafers': Select2MultipleWidget(),
        }
                
    def __init__(self, *args, **kwargs):
        super(TestplanForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['notes'].required = False
        self.fields['primary_contact'].required = False
        

class FoundryForm(forms.ModelForm):
    
    class Meta:
        model = Foundry
        fields = ['name']
    
        
class ProcessForm(forms.ModelForm):
    
    class Meta:
        model = Process
        fields = ['foundry', 'name']
        widgets = {
            'foundry': forms.HiddenInput()
        }
        
class WaferForm(forms.ModelForm):
        
    class Meta:
        model = Wafer
        fields = ('name', 'process')
        widgets = {
            'process': forms.HiddenInput()
        }
