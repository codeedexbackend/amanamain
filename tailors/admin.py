from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
# Register your models here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import AddCustomer
from .utils import render_to_pdf 
from .models import  AddCustomer, Order,AddTailor,WorkStatus

class AddCustomerInline(admin.StackedInline):
    model = AddCustomer
    can_delete = False
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/print/', self.admin_site.admin_view(self.print_view), name='measurement_print'),
        ]
        return custom_urls + urls

    def print_view(self, request, object_id, *args, **kwargs):
        add_customer = get_object_or_404(AddCustomer, id=object_id)
        pdf = render_to_pdf('tailors/print_measurement.html', {'add_customer': add_customer})
        return HttpResponse(pdf, content_type='application/pdf')

class OrderInline(admin.TabularInline):
    model = Order


class AddCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'length', 'shoulder', 'sleeve', 'loose', 'neck', 'regal', 'cuf', 'print_button')
    
    def print_button(self, obj):
        # Use the actual URL without 'admin:' prefix
        print_url = reverse('measurement_print', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Print</a>', print_url)
    
    print_button.short_description = 'Print'

admin.site.register(AddCustomer, AddCustomerAdmin)

admin.site.register(Order)
admin.site.register(AddTailor)
admin.site.register(WorkStatus)


# admin.site.register(Measurement)