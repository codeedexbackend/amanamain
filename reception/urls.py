from django.urls import path

from reception import views

urlpatterns = [
    path('reception_indexpage/', views.reception_indexpage, name='reception_indexpage'),
    path("createcustomer_reception/", views.createcustomer_reception, name="createcustomer_reception"),
    path('search_mobile_recption/', views.search_mobile_recption, name='search_mobile_recption'),
    path("add_order_recption/<int:dataid>/", views.add_order_recption, name="add_order_recption"),
    path("edit_order_reception/<int:dataid>/", views.edit_order_reception, name="edit_order_reception"),
    path("update_add_order_reception/<int:dataid>/", views.update_add_order_reception, name="update_add_order_reception"),
    path("edit_customer_recption/<int:dataid>/", views.edit_customer_recption, name="edit_customer_recption"),
    path("save_add_order_recption/", views.save_add_order_recption, name="save_add_order_recption"),
    path("update_customer_recption/<int:dataid>/", views.update_customer_recption, name="update_customer_recption"),

    path("customerdlt_recption/<int:dlt>/", views.customerdlt_recption, name="customerdlt_recption"),
    path("orderdlt_reception/<int:dlt>/", views.orderdlt_reception, name="orderdlt_reception"),
    path("customer_details_recption/", views.customer_details_recption, name="customer_details_recption"),
    path("single_customer_reception/<int:customer_id>/", views.single_customer_reception, name="single_customer_reception"),
    path("tailor_details_recption/", views.tailor_details_recption, name="tailor_details_recption"),
    # path("additems_reception/<int:dataid>/", views.additems_reception, name="additems_reception"),
    path("order_add_item/<int:dataid>/", views.order_add_item, name="order_add_item"),
    path("order_details_reception/", views.order_details_reception, name="order_details_reception"),
    path("save_items_recption/", views.save_items_recption, name="save_items_recption"),
    path("savecustomer_recption/", views.savecustomer_recption, name="savecustomer_recption"),
    path('select_dates_recption/', views.select_dates_recption, name='select_dates_recption'),
    path('tailor_work_details_recption/', views.tailor_work_details_recption, name='tailor_work_details_recption'),
    path('customer_bill/<int:customer_id>/', views.customer_bill_reception, name='customer_bill'),
    path('generate_pdf/<int:customer_id>/', views.print_measurement_reception, name='generate_pdf'),

    path('check_tailor_works_recption/', views.check_tailor_works_recption, name='check_tailor_works_recption'),
    path('fetch_tailor_options_recption/', views.fetch_tailor_options_recption, name='fetch_tailor_options_recption'),


    # apilinks
    path('tailor/<int:tailor_id>/order/<int:id>/inprogress-to-completed/', views.InProgressToCompletedAPIView.as_view(),name='inprogress_to_completed'),

    path('tailor/login/', views.TailorLoginView.as_view(), name='tailor-login'),
    path('tailor/<int:tailor_id>/assigned_works/', views.TailorAssignedWorksAPIView.as_view(),name='tailor-assigned-works'),
    path('tailor/<int:tailor_id>/completed-works/', views.CompletedOrderListAPIView.as_view(),name='completed_works_list'),

    path('order/<int:order_id>/items/', views.ItemListAPIView.as_view(), name='item_list'),

    path('tailor/<int:tailor_id>/inprogress-works/', views.InProgressWorksAPIView.as_view(), name='inprogress-works'),
    path('tailor/<int:tailor_id>/order/<int:id>/inprogress/', views.AssignedToInProgressAPIView.as_view(),name='assigned-to-inprogress'),

]
