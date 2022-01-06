from django.contrib import admin
from .models import ApiKeyModel, AutoBalancerModel
import schedule
import time
import datetime
from django.shortcuts import redirect
from django_object_actions import DjangoObjectActions
from .script import AutoBalancerMainFun

def running_process(obj):
    balacer = obj

    obj.is_runing = True
    obj.save()            

    def printTime():
        print("Time --> ", datetime.datetime.now())

    AutoBalancerMainFun(
        api_token=balacer.key, 
        loadbalancer_tag=balacer.loadbalancer_tag,
        droplet_tag=balacer.droplet_tag,
        max_drop=balacer.maximum_droplets,
        min_drop=balacer.minimun_droplets,
        cpu=balacer.threshold_CPU,
        load1=balacer.threshold_Load1,
        load5=balacer.threshold_load5,
        load15=balacer.threshold_load15
    )

    schedule.every(5).seconds.do(printTime).tag(f'auto{balacer.id}')
    schedule.every(1).minutes.do(AutoBalancerMainFun, api_token=balacer.key, 
        loadbalancer_tag=balacer.loadbalancer_tag,
        droplet_tag=balacer.droplet_tag,
        max_drop=balacer.maximum_droplets,
        min_drop=balacer.minimun_droplets,
        cpu=balacer.threshold_CPU,
        load1=balacer.threshold_Load1,
        load5=balacer.threshold_load5,
        load15=balacer.threshold_load15
    ).tag(f'auto{balacer.id}')

    while True:
        schedule.run_pending()
        time.sleep(1)

class ApiKeyModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'created_at']


class AutoBalancerModelAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['id', 'loadbalancer_name', 'loadbalancer_tag', 'droplet_tag', 'is_runing', 'threshold_CPU', 'threshold_Load1', 'threshold_load5', 'threshold_load15', 'created_at', 'minimun_droplets', 'maximum_droplets', 'key']
    
    def RUN_BALANCER(self, request, obj):
        if obj.is_runing == False:

            running_process(obj=obj)

        else:
            obj.is_runing = False
            obj.save()
            schedule.clear(f'auto{obj.id}')



    RUN_BALANCER.label = "RUN OR STOP Auto Balancer" 

    # def STOP_BALANCER(self, request, obj):
    #     obj.is_running = False
    #     obj.save()
    #     print(obj.is_runing)

    change_actions = ('RUN_BALANCER', )

admin.site.register(ApiKeyModel, ApiKeyModelAdmin)
admin.site.register(AutoBalancerModel, AutoBalancerModelAdmin)
