from __future__ import absolute_import, unicode_literals
from celery import task
import requests
from .models import Setting
from ..settings import SMART_HOME_ACCESS_TOKEN


@task()
def smart_home_manager() :
    request = dict()
    request['controllers'] = []
    TOKEN = SMART_HOME_ACCESS_TOKEN
    try :
        data = requests.get('https://smarthome.webpython.graders.eldf.ru/api/user.controller',
                            headers={'Authorization' : f'Bearer {TOKEN}'}).json()
        if data['status'] == 'ok':
            data = data['data']
            temp_dict = {}
            for value in data :
                temp_dict[value['name']] = value['value']
            bedroom_temperature = Setting.objects.get(controller_name='bedroom_temperature').value
            hotwater_temperature = Setting.objects.get(controller_name='hot_water_temperature').value
            bedroom_light = Setting.objects.get(controller_name='bedroom_light').value
            bathroom_light = Setting.objects.get(controller_name='bathroom_light').value

            requests.post('https://smarthome.webpython.graders.eldf.ru/api/user.controller', json=request,
                          headers={'Authorization' : f'Bearer {TOKEN}'})
    except requests.exceptions.ConnectionError:
        pass
