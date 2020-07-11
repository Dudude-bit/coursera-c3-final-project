from __future__ import absolute_import, unicode_literals
from celery import task
import requests
from django.core.mail import send_mail
from django.http import HttpResponse

from .models import Setting
from ..settings import EMAIL_RECEPIENT, SMART_HOME_ACCESS_TOKEN


@task()
def smart_home_manager() :
    request = dict()
    request['controllers'] = []
    TOKEN = SMART_HOME_ACCESS_TOKEN
    try :
        data = requests.get('https://smarthome.webpython.graders.eldf.ru/api/user.controller',
                            headers={'Authorization' : f'Bearer {TOKEN}'}).json()['data']
        temp_dict = {}
        for value in data :
            temp_dict[value['name']] = value['value']
        bedroom_temperature = Setting.objects.get(controller_name='bedroom_temperature').value
        hotwater_temperature = Setting.objects.get(controller_name='hot_water_temperature').value
        bedroom_light = Setting.objects.get(controller_name='bedroom_light').value
        bathroom_light = Setting.objects.get(controller_name='bathroom_light').value
        requests.post('https://smarthome.webpython.graders.eldf.ru/api/user.controller', json=request,
                      headers={'Authorization' : f'Bearer {TOKEN}'})
        if temp_dict['leak_detector'] :
            send_mail(subject='Протечка', message='Обнаружена протечка', from_email='kirillinyakin@yandex.ru',
                      recipient_list=[EMAIL_RECEPIENT])
            request['controllers'].append({
                'name' : 'cold_water',
                'value' : False
            })
            request['controllers'].append({
                'name' : 'hot_water',
                'value' : False
            })
            request['controllers'].append({
                'name' : 'boiler',
                'value' : False
            })
            request['controllers'].append({
                'name' : 'washing_machine',
                'value' : 'off'
            })
        elif temp_dict['cold_water'] == False :
            request['controllers'].append({
                'name' : 'boiler',
                'value' : False
            })
            request['controllers'].append({
                'name' : 'washing_machine',
                'value' : 'off'
            })
        elif temp_dict['boiler_temperature'] and 0.9 * int(
                temp_dict['boiler_temperature']) < hotwater_temperature and not (temp_dict['cold_water']) :
            request['controllers'].append({
                'name' : 'boiler',
                'value' : True
            })
        elif temp_dict['boiler_temperature'] and 1.1 * int(temp_dict['boiler_temperature']) > hotwater_temperature :
            request['controllers'].append({
                'name' : 'boiler',
                'value' : False
            })
        elif int(temp_dict['outdoor_light'] < 50) and not (temp_dict['curtains'] == 'slightly_open') and not (
                temp_dict['bedroom_light']) :
            request['controllers'].append({
                'name' : 'curtains',
                'value' : 'open'
            })
        elif (int(temp_dict['outdoor_light'] > 50) or temp_dict[
            'bedroom_light']) and not (temp_dict['curtains'] == 'slightly_open') :
            request['controllers'].append({
                'name' : 'curtains',
                'value' : 'open'
            })
        requests.post('https://smarthome.webpython.graders.eldf.ru/api/user.controller', json=request,
                      headers={'Authorization' : f'Bearer {TOKEN}'})
    except requests.exceptions.ConnectionError:
        pass
