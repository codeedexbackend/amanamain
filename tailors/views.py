# tailors/views.py
from django.views.generic import TemplateView

from django.shortcuts import render, get_object_or_404,redirect
from .models import  Order, AddTailor, AddCustomer
from .forms import OrderForm, TailorForm,TailorSelectionForm
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from xhtml2pdf import pisa
from .utils import render_to_pdf, generate_bill_number
from rest_framework import generics



def list_customers(request):
    customers = AddCustomer.objects.all()
    return render(request, 'Customer_details.html', {'customers': customers})

def customer_detail(request, customer_id):
    customer = get_object_or_404(AddCustomer, pk=customer_id)
    return render(request, 'tailors/customer_detail.html', {'customer': customer})

def create_order(request, customer_id):
    customer = get_object_or_404(AddCustomer, pk=customer_id)
    tailors = AddTailor.objects.all()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.addcustomer = customer
            order.save()
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = OrderForm()

    return render(request, 'tailors/create_order.html', {'customer': customer, 'form': form, 'tailors': tailors})

@login_required
def create_tailor(request):
    if request.method == 'POST':
        form = TailorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TailorForm()

    return render(request, 'tailors/tailor_create.html', {'form': form})


class DashboardView(TemplateView):
    template_name = 'tailors/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve data for the dashboard
        total_customers = AddCustomer.objects.count()
        total_measurements = AddCustomer.objects.count()
        total_tailors = AddTailor.objects.count()
        total_orders = Order.objects.count()

        # You can add more logic to retrieve additional data as needed

        context['total_customers'] = total_customers
        context['total_measurements'] = total_measurements
        context['total_tailors'] = total_tailors
        context['total_orders'] = total_orders
        # Add more data to the context as needed

        context['recent_orders'] = Order.objects.order_by('-order_date')[:5]
        context['recent_tailors'] = AddTailor.objects.order_by('-id')[:5]
        # Add more data to the context as needed

        return context


def select_tailor_and_print_measurement(request, measurement_id):
    measurement = AddCustomer.objects.get(id=measurement_id)

    if request.method == 'POST':
        form = TailorSelectionForm(request.POST)
        if form.is_valid():
            tailor = form.cleaned_data['tailor']
            measurement.tailor = tailor
            measurement.save()
            return render(request, 'tailors/print_measurement.html', {'measurement': measurement})
    else:
        form = TailorSelectionForm()

    return render(request, 'tailors/select_tailor.html', {'form': form, 'measurement': measurement})

def print_measurement(request, measurement_id):
    measurement = AddCustomer.objects.get(pk=measurement_id)
    # Add any additional logic or context data needed for printing
    context = {'measurement': measurement}
    return render(request, 'tailors/print_measurement.html', context)


class MeasurementPDFView(View):
    def get(self, request, *args, **kwargs):
        measurement_id = kwargs.get('measurement_id')
        measurement = AddCustomer.objects.get(pk=measurement_id)

        # Retrieve associated order for additional information
        order = Order.objects.filter(customer=measurement).first()

        context = {'measurement': measurement, 'order': order}

 
        template_path = 'tailors/print_measurement.html'
        template = get_template(template_path)
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={measurement.name.replace(" ", "_")}.pdf'

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', content_type='text/plain')
        return response
    
def customer_orders(request, phone_number):
    customer = get_object_or_404(AddCustomer, phone_number=phone_number)
    orders = Order.objects.filter(customer=customer)
    
    context = {
        'customer': customer,
        'orders': orders, 
    }

    return render(request, 'tailors/customer_orders.html', context)

def print_measurement(request, measurement_id):
    measurement = get_object_or_404(AddCustomer, pk=measurement_id)

    # Fetch the associated order for the measurement
    order = Order.objects.filter(customer=measurement).first()

    # Add any additional logic or context data needed for printing
    context = {
        'measurement': measurement,
        'order': order,  # Pass the order to the context
    }

    return render(request, 'tailors/print_measurement.html', context)


def tailor_list(request):
    tailors = AddTailor.objects.all()
    context = {'tailors': tailors}
    return render(request, 'tailors/tailor_list.html', context)



def view_orders(request):
    mobile_number = request.GET.get('mobile_number', '')
    status = request.GET.get('status', '')

    orders = AddCustomer.objects.all()

    if mobile_number:
        orders = orders.filter(phone_number__icontains=mobile_number)

    if status:
        orders = orders.filter(work_status__status=status)

    context = {'orders': orders}
    return render(request, 'tailors/view_orders.html', context)
