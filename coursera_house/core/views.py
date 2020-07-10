from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from .models import Setting
from .form import ControllerForm
import requests

from ..settings import SMART_HOME_API_URL, SMART_HOME_ACCESS_TOKEN


class ControllerView(View):
    def get(self, request):
        TOKEN = SMART_HOME_ACCESS_TOKEN
        try:
            requests.get(SMART_HOME_API_URL, headers={'Authorization' : f'Bearer {TOKEN}'})
        except requests.exceptions.ConnectionError:
            return HttpResponse(status=502)
        context = dict()
        data = Setting.objects.all()
        context['data'] = {v.controller_name : v.value for v in data}
        form = ControllerForm
        context['form'] = form
        return render(request, 'core/control.html', context=context)

    def post(self, request):
        TOKEN = SMART_HOME_ACCESS_TOKEN
        try:
            requests.get(SMART_HOME_API_URL, headers={'Authorization' : f'Bearer {TOKEN}'})
        except requests.exceptions.ConnectionError:
            return HttpResponse(status=502)
        form = ControllerForm(request.POST)
        if form.is_valid():
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
                'value' : 1 if bathroom_light == 'off' else 0
            }, controller_name='bathroom_light', label='bathroom_light')
        context = dict()
        data = Setting.objects.all()
        context['data'] = {v.controller_name : v.value for v in data}
        form = ControllerForm
        context['form'] = form
        return render(request, 'core/control.html', context=context)