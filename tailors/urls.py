from django.urls import path
from .views import DashboardView, list_customers, customer_detail, create_order, select_tailor_and_print_measurement, print_measurement,MeasurementPDFView,customer_orders,create_tailor,tailor_list,view_orders # Import views

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('customers/', list_customers, name='list_customers'),
    path('customer/<int:customer_id>/', customer_detail, name='customer_detail'),
    path('customer/<int:customer_id>/create_order/', create_order, name='create_order'),
    path('create_tailor/', create_tailor, name='create_tailor'),
    path('measurement/<int:measurement_id>/select_tailor/', select_tailor_and_print_measurement, name='select_tailor'),
    path('measurement/<int:measurement_id>/print/', print_measurement, name='measurement_print'),
    path('measurement/<int:measurement_id>/pdf/', MeasurementPDFView.as_view(), name='measurement_pdf'),
    path('customer/<str:mobile_number>/orders/', customer_orders, name='customer_orders'),
    path('tailor-list/', tailor_list, name='tailor-list'),
    path('view-orders/', view_orders, name='view_orders'),



]
