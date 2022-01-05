from django.contrib import admin
from .models import ApiKeyModel, AutoBalancerModel

class ApiKeyModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'created_at']


class AutoBalancerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'loadbalancer_name', 'loadbalancer_tag', 'droplet_tag', 'threshold_CPU', 'threshold_Load1', 'threshold_load5', 'threshold_load15', 'created_at', 'minimun_droplets', 'maximum_droplets']


admin.site.register(ApiKeyModel, ApiKeyModelAdmin)
admin.site.register(AutoBalancerModel, AutoBalancerModelAdmin)
