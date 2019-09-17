from django.http import HttpResponse, HttpResponseBadRequest
from .forms import WaferForm, ProcessForm, FoundryForm
import requests
import json
import mimetypes
import os
import logging
from django.conf import settings


def save_new_object(request):
    # New wafer submission
    if 'submit-wafer' in request.POST:
        form = WaferForm(request.POST, prefix="wafer")

    # New foundry submission
    elif 'submit-foundry' in request.POST:
        form = FoundryForm(request.POST, prefix="foundry")
            
    # New process submission
    elif 'submit-process' in request.POST:
        form = ProcessForm(request.POST, prefix="process")
    
    # Do nothing (http 204 response) for unexpected/unknown POST requests
    else:
        return 204, None
        
    # Save and return new object or return http 400 response if form is invalid
    if form.is_valid():
        new_obj = form.save()
        return None, new_obj
    else:
        return 400, None


def create_restyaboard_card(testplan):
    token = restyaboard_login()
    
    # Hard-coded Test Queue board ID and list IDs as of 9/5/19
    Test_Queue_Board_ID = #####
    Backlog_ID = '#####'
    Priority_1_ID = '#####'
    Priority_2_ID = '#####'
    WIP_ID = '#####'
    Done_ID = '#####'
    
    if testplan.status == 'backlog':
        listID = Backlog_ID
    elif testplan.status == 'priority_1':
        listID = Priority_1_ID
    elif testplan.status == 'priority_2':
        listID = Priority_2_ID
    elif testplan.status == 'wip':
        listID = WIP_ID
    elif testplan.status == 'done':
        listID = Done_ID
    else:
        print 'failed!'
        return 1
        
    card_name = str(testplan.foundry) + ' ' + str(testplan.process) + ' wafers '
    for wafer in testplan.wafers.all():
        card_name = card_name + str(wafer) + ', '
    card_name = card_name[:-2]
    
    # Create card
    data = {
        "board_id": Test_Queue_Board_ID,
        "list_id": listID,
        "name": card_name,
        "position": 0
    }
    card_id = requests.post('http://#####/restyaboard/api/v1/boards/' + str(Test_Queue_Board_ID) + '/lists/' + str(listID) + '/cards.json?token=' + token, json=data).json()['id']
    
    card_url = 'http://#####/restyaboard/api/v1/boards/' + str(Test_Queue_Board_ID) + '/lists/' + str(listID) + '/cards/' + card_id
    
    # Add testplan link as card comment
    data = { "description": "[View details here](" + testplan.get_absolute_url() + ")" }
    response = requests.put(card_url + '.json?token=' + token, json=data)
    
    restyaboard_logout(token)


def restyaboard_login():
    guest_token = requests.get('http://#####/api/v1/oauth.json').json()['access_token']
    token  = requests.post('http://#####/restyaboard/api/v1/users/login.json?token=' + guest_token, json={"email": "#####", "password": "#####"}).json()['access_token']
    return token

def restyaboard_logout(token):
    logout_response = requests.get('http://#####/restyaboard/api/v1/users/logout.json?token=' + token)    
    