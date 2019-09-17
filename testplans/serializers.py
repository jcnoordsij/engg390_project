from rest_framework import serializers
from .models import Testplan

class TestplanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testplan
        fields = ['primary_contact', 'status', 'archived']
