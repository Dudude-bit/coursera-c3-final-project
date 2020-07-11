from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm
import requests

from ..settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN


class ControllerView(FormView) :
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    TOKEN = SMART_HOME_ACCESS_TOKEN

    def get(self, request, *args, **kwargs) :
        TOKEN = SMART_HOME_ACCESS_TOKEN
        try :
            requests.get('https://smarthome.webpython.graders.eldf.ru/api/user.controller',
                         headers={'Authorization' : f'Bearer {TOKEN}'}).json()['data']
        except requests.exceptions.ConnectionError :
            return HttpResponse(status=502)
        return super(ControllerView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) :
        TOKEN = SMART_HOME_ACCESS_TOKEN
        try :
            data = requests.get('https://smarthome.webpython.graders.eldf.ru/api/user.controller',
                                headers={'Authorization' : f'Bearer {TOKEN}'}).json()
            if data['status'] != 'ok' :
                return HttpResponse(status=502)
            else :
                hotwater_temperature = request.POST.get('hot_water_target_temperature')
                data = data['data']
                temp_dict = {}
                for value in data :
                    temp_dict[value['name']] = value['value']
                if temp_dict['boiler_temperature'] and 0.9 * int(
                        temp_dict['boiler_temperature']) < hotwater_temperature and not (temp_dict['cold_water']) :
                    request['controllers'].append({
                        'name' : 'boiler',
                        'value' : True
                    })
                elif temp_dict['boiler_temperature'] and 1.1 * int(
                        temp_dict['boiler_temperature']) > hotwater_temperature :
                    request['controllers'].append({
                        'name' : 'boiler',
                        'value' : False
                    })
        except requests.exceptions.ConnectionError :
            return HttpResponse(status=502)
        return super(ControllerView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs) :
        context = super(ControllerView, self).get_context_data()
        data = Setting.objects.all()
        context['data'] = {v.controller_name : v.value for v in data}
        return context

    def get_initial(self) :
        try :
            bedroom_temperature = Setting.objects.get(controller_name='bedroom_temperature').value
            bathroom_temperature = Setting.objects.get(controller_name='hot_water_temperature').value
        except Setting.DoesNotExist :
            bedroom_temperature = Setting.objects.create(controller_name='bedroom_temperature',
                                                         label='bedroom_target_temperature').value
            bathroom_temperature = Setting.objects.create(controller_name='hot_water_temperature',
                                                          label='hot_water_target_temperature').value
        return {'bedroom_target_temperature' : bedroom_temperature,
                'hot_water_target_temperature' : bathroom_temperature}

    def form_valid(self, form) :
        bedroom_temperature = self.request.POST.get('bedroom_target_temperature')
        hot_water = self.request.POST.get('hot_water_target_temperature')
        bedroom_light = self.request.POST.get('bedroom_light')
        bathroom_light = self.request.POST.get('bathroom_light')
        Setting.objects.update_or_create(defaults={'value' :
                                                       bedroom_temperature}, controller_name='bedroom_temperature',
                                         label='bedroom_target_temperature')
        Setting.objects.update_or_create(defaults={
            'value' : hot_water
        }, controller_name='hot_water_temperature', label='hot_water_target_temperature')
        Setting.objects.update_or_create(defaults={
            'value' : 1 if bedroom_light == 'on' else 0
        }, controller_name='bedroom_light', label='bedroom_light')
        Setting.objects.update_or_create(defaults={
            'value' : 1 if bathroom_light == 'on' else 0
        }, controller_name='bathroom_light', label='bathroom_light')
        return super(ControllerView, self).form_valid(form)
