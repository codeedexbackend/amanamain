# from tailors.models import AddCustomer
import logging
import random
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from xhtml2pdf import pisa

from reception.views import reception_indexpage
from .models import AddTailors
from .models import Customer, Item, reception_login, admin_login, Add_order
from .serializers import TailorLoginSerializer, CustomerSerializer, CompletedCustomerSerializer


class TailorLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TailorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        print(f"Attempting to authenticate user: {username}")

        user = authenticate(request, username=username, password=password)

        try:
            user = AddTailors.objects.get(username=username, password=password)
        except AddTailors.DoesNotExist:
            user = None

        if user:
            print(f"Authentication successful for user: {username}")
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            response_data = {
                'message': 'Authentication successful',
                'status': True,
                'token': token,
                'user_id': user.id,
                'username': user.username,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print(f"Authentication failed for user: {username}")
            response_data = {
                'error': 'Invalid credentials',
                'status': False,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class CustomerListAPIView(ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, status='assigned')

    def perform_create(self, serializer):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)

        customer_instance = serializer.save(tailor=tailor, status='assigned')

        tailor.refresh_from_db()
        tailor.assigned_works += 1
        tailor.save()

        return customer_instance


class InProgressCustomerUpdateAPIView(UpdateAPIView):
    serializer_class = CustomerSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, id=customer_id, status='assigned')

    def perform_update(self, serializer):
        serializer.save(status='in_progress')

        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']

        tailor = get_object_or_404(AddTailors, id=tailor_id)

        if tailor.assigned_works > 0:
            tailor.assigned_works -= 1
            tailor.save()

        tailor.pending_works += 1
        tailor.save()

        return Response({'status': True}, status=status.HTTP_200_OK)


class InProgressToCompletedAPIView(UpdateAPIView):
    serializer_class = CustomerSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, id=customer_id, status='in_progress')

    def perform_update(self, serializer):
        serializer.save(status='completed')

        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']

        tailor = get_object_or_404(AddTailors, id=tailor_id)

        tailor.pending_works -= 1
        tailor.save()

        tailor.completed_works += 1
        tailor.save()

        return Response({'status': True}, status=status.HTTP_200_OK)


class InProgressCustomerListAPIView(ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, status='in_progress')


class CustomerDetailAPIView(RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_object(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['pk']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return get_object_or_404(Customer, pk=customer_id, tailor=tailor)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_changed = False

        if 'status' in serializer.validated_data:
            current_status = self.get_object().status
            new_status = serializer.validated_data['status']

            if current_status != new_status:
                status_changed = True
                serializer.save(status=new_status)

        response_data = {
            'status_changed': status_changed,
            'status': True,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CompletedCustomerListAPIView(ListAPIView):
    serializer_class = CompletedCustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        return Customer.objects.filter(tailor_id=tailor_id, status='completed')


def indexpage(request):
    return render(request, "dashboard.html")


def createcustomer(request):
    tailor = AddTailors.objects.all()
    tailor_works = []
    for tailor in tailor:
        assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        pending_works = tailor.pending_works  # Assuming you have a pending_works field in AddTailors
        tailor_works.append({'tailor': tailor, 'assigned_works': assigned_works, 'pending_works': pending_works})

    context = {'tailor_works': tailor_works}
    return render(request, 'Create_customer.html', context)


def addtailors(request):
    return render(request, "Add_tailor.html")


def save_tailor(request):
    if request.method == "POST":
        tn = request.POST.get('tname')
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        mob = request.POST.get('mobile')
        obj = AddTailors(tailor=tn, username=un, password=pwd, mobile_number=mob)
        obj.save()
        messages.success(request, "Tailor Added Successfully")
    return redirect(addtailors)


def view_tailors(request):
    return render(request, "View_Tailor.html")


def tailor_details(request):
    tailors = AddTailors.objects.all()

    for tailor in tailors:
        # Calculate assigned, pending, upcoming, and completed works
        tailor.assigned_works = Add_order.objects.filter(tailor=tailor, status='assigned').count()
        tailor.pending_works = Add_order.objects.filter(tailor=tailor, status='in_progress').count()
        tailor.upcoming_works = Add_order.objects.filter(tailor=tailor, delivery_date__gt=date.today()).count()
        tailor.completed_works = Add_order.objects.filter(tailor=tailor, status='completed').count()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor.html', context)


def additems(request, dataid):
    order = Add_order.objects.get(id=dataid)
    return render(request, "Add_items_admin.html", {"customers": order})


def additem(request, dataid):
    order = Add_order.objects.get(id=dataid)
    return render(request, "Add_items.html", {'order': order})


def save_items(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderid')
        customer = request.POST.get('customerid')
        item_names = request.POST.getlist('itemName[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('price[]')

        order_instance = Add_order.objects.get(id=order_id)
        customer_instance = Customer.objects.get(id=customer)

        for i in range(len(item_names)):
            if i < len(quantities) and i < len(prices):
                item = Item(
                    order_id=order_instance,
                    customer=customer_instance,
                    item_name=item_names[i],
                    item_quantity=int(quantities[i]),
                    item_price=float(prices[i])
                )
                item.save()
            else:
                print(f"Skipping item at index {i} due to incomplete data.")

        return redirect('customer_details')


def customer_details(request):
    cus = Customer.objects.all()
    return render(request, "Customer_Details.html", {"cus": cus})


def order_details(request):
    cus = Add_order.objects.all()
    return render(request, "Order_Details.html", {"cus": cus})


def upcoming_deliveries(request):
    cus = Customer.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    return render(request, 'dashboard.html', {'cus': cus})


def check_tailor_works(request):
    if request.method == 'GET':
        tailor_id = request.GET.get('tailor_id')
        delivery_date = request.GET.get('delivery_date')

        try:
            # Assuming you have a Customer model with a tailor field
            works = Customer.objects.filter(tailor__id=tailor_id, delivery_date=delivery_date)

            # You may need to serialize the works data based on your requirements
            serialized_works = [{'name': work.name, 'other_field': work.other_field} for work in works]

            return JsonResponse({'works': serialized_works})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def fetch_tailor_options(request):
    if request.method == 'GET' and 'delivery_date' in request.GET:
        delivery_date = request.GET.get('delivery_date')

        try:
            tailors = AddTailors.objects.all()
            tailor_options = []

            for tailor in tailors:
                try:
                    # Access the related set of Customer objects using customer_set
                    works_on_date = tailor.add_order_set.filter(delivery_date=delivery_date)

                    # Count assigned and pending works separately
                    assigned_works = works_on_date.filter(status='assigned').count()
                    pending_works = works_on_date.filter(status='pending').count()

                    tailor_options.append({
                        'id': tailor.id,
                        'name': tailor.tailor,
                        'assigned_works': assigned_works,
                        'pending_works': pending_works,
                    })
                except Exception as e:
                    print(f"Error processing tailor {tailor.id}: {str(e)}")

            return JsonResponse({'tailor_options': tailor_options})

        except Exception as e:
            # Print the error details to the console
            import traceback
            print(traceback.format_exc())

            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def savecustomer(request):
    context = {}

    if request.method == "POST":
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve')
        sll = request.POST.get('sleeve_length')
        nc = request.POST.get('neck')
        wr = request.POST.get('wrist')
        ncr = request.POST.get('neck_round')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('bottom2')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        ds = request.POST.get('description')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('Cloth')

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        if works_on_delivery_date >= 6:
            error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
            if request.is_ajax():
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.error(request, error_message)
                return redirect(createcustomer)

        tailor_instance.assigned_works += 1
        tailor_instance.save()

        try:
            # Generate a unique bill_number (you can customize this logic)
            random_3_digits = random.randint(0, 999)
            bill_number = f"{timezone.now().strftime('%Y%m%d')}{random_3_digits:03d}"

            obj = Customer(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg, cuff_length=cl,
                           cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
                           order_date=od, cloth=cloth, delivery_date=dd, tailor=tailor_instance, button_type=bt,
                           neck_round=ncr, wrist=wr, collar=clr, description=ds, bill_number=bill_number)
            obj.save()

            add_order_obj = Add_order(customer_id=obj, length=ln, shoulder=sd, cloth=cloth, sleeve_type=sl,
                                      sleeve_length=sll, neck=nc, neck_round=ncr, collar=clr, regal=rg, loose=lo,
                                      wrist=wr, pocket=po, cuff_length=cl, bottom1=b1, bottom2=b2, button_type=bt,
                                      order_date=od, delivery_date=dd, tailor=tailor_instance, description=ds,
                                      bill_number=bill_number)
            add_order_obj.save()

            messages.success(request, "Successfully added customer")
            return redirect(createcustomer)
        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return render(request, 'Create_customer.html', context)


@api_view(['POST'])
def accept_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)

    # Update the pending works count
    tailor.pending_works += 1
    tailor.save()

    return Response({'status': 'Pending works updated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def complete_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)

    # Update the pending and completed works counts
    if tailor.pending_works > 0:
        tailor.pending_works -= 1
        tailor.completed_works += 1
        tailor.save()
        return Response({'status': 'Work completed successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'No pending works to complete'}, status=status.HTTP_400_BAD_REQUEST)


def customerdlt(request, dlt):
    delt = Customer.objects.filter(id=dlt)
    delt.delete()
    return redirect(customer_details)


def orderdlt(request, dlt):
    delt = Add_order.objects.filter(id=dlt)
    id = Add_order.objects.get(id=dlt)
    id_dlt = id.tailor.id
    delt.delete()
    tailor_instance = AddTailors.objects.get(id=id_dlt)
    tailor_instance.assigned_works -= 1
    tailor_instance.save()
    return redirect(order_details)


def dashboard(request):
    total_customers = Customer.objects.count()
    total_order = Add_order.objects.count()  # Assuming you have an Order model

    total_completed_works = AddTailors.objects.aggregate(Sum('completed_works'))['completed_works__sum']

    cus = Add_order.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    context = {'total_customers': total_customers, 'total_orders': total_order,
               'cus': cus,
               'total_completed_works': total_completed_works}

    return render(request, 'dashboard.html', context)


logger = logging.getLogger(__name__)

def customer_bill(request, customer_id):
    order = Add_order.objects.filter(id=customer_id)
    item = Item.objects.filter(order_id=customer_id)

    return render(request, 'Print_measurements.html', {'order':order, 'item':item})

def print_measurement(request, customer_id):
    customer = Add_order.objects.get( id=customer_id)

    context = {'customer': customer}

    template_path = 'Print_measurements.html'
    template = get_template(template_path)
    html = template.render(context)

    # Debugging: Print HTML to console
    print(html)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=measurement_{customer_id}.pdf'

    # Create PDF from HTML content
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response





def tailor_details(request):
    tailors = AddTailors.objects.all()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor.html', context)


def all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})


def edit_tailor(request, dataid):
    tail = AddTailors.objects.get(id=dataid)
    return render(request, "edit_tailor.html", {"tail": tail})


def updatetailor(request, dataid):
    if request.method == "POST":
        tn = request.POST.get('tname')
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        mob = request.POST.get('mobile')
        AddTailors.objects.filter(id=dataid).update(tailor=tn, username=un, password=pwd, mobile_number=mob)
        messages.success(request, "Tailor Details Updated Successfully...!")
    return redirect(tailor_details)


def delete_tailor(request, dataid):
    tailor = get_object_or_404(AddTailors, pk=dataid)

    # Add your logic for deleting tailor here
    tailor.delete()

    return redirect('view_tailors')


def edit_customer(request, dataid):
    ed = Customer.objects.all()
    cus = Customer.objects.get(id=dataid)
    return render(request, "edit_customer.html", {"cus": cus, "ed": ed})


def update_customer(request, dataid):
    if request.method == "POST":
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve')
        sll = request.POST.get('sleeve_length')
        nc = request.POST.get('neck')
        wr = request.POST.get('wrist')
        ncr = request.POST.get('neck_round')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('bottom2')
        od = request.POST.get('order_date')
        cloth = request.POST.get('cloth')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        other = request.POST.get('other')

        # Get the existing customer
        customer = Customer.objects.get(id=dataid)

        # Update the customer instance
        Customer.objects.filter(id=dataid).update(
            name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc,
            regal=rg, cuff_length=cl, cuff_type=ct, sleeve_type=sl,
            sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2, cloth=cloth, button_type=bt,
            neck_round=ncr, wrist=wr, collar=clr, description=other
        )
        messages.success(request, "Customer Details Updated Successfully...!")

    return redirect('customer_details')


def search_mobile(request):
    results = {'Customer': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']

        results['customer'] = Customer.objects.filter(mobile__icontains=query).exclude(mobile__isnull=True).exclude(
            mobile__exact='')

    return render(request, 'search.html', {'results': results, 'query': query})


def single_customer(request, customer_id):
    single = Customer.objects.filter(id=customer_id)
    view_add_order = Add_order.objects.filter(customer_id=customer_id)
    itms = Item.objects.filter(customer_id=customer_id)
    return render(request, "single_customer.html", {'single': single, 'itms': itms, 'view': view_add_order})


def add_order(request, dataid):
    add = Customer.objects.get(id=dataid)
    return render(request, "Add_order.html", {"add": add})


def edit_order(request, dataid):
    add = Add_order.objects.get(id=dataid)
    return render(request, "edit_order.html", {"add": add})


def update_add_order(request, dataid):
    if request.method == "POST":
        # Your existing form processing logic
        id = request.POST.get('id')
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve')
        sll = request.POST.get('sleeve_length')
        nc = request.POST.get('neck')
        wr = request.POST.get('wrist')
        ncr = request.POST.get('neck_round')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('bottom2')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('cloth')
        other = request.POST.get('other')
        # Get the existing customer
        customer = Add_order.objects.get(id=dataid)

        # Get the old tailor before updating
        old_tailor = customer.tailor

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        if works_on_delivery_date >= 6:
            error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
            if request.is_ajax():
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.error(request, error_message)
                return redirect(order_details)
                # Get or create the new tailor instance
        new_tailor = AddTailors.objects.get(id=tailor_id)

        # Update assigned_works for the old tailor and new tailor
        if old_tailor != new_tailor:
            old_tailor.assigned_works -= 1
            old_tailor.save()
            new_tailor.assigned_works += 1
            new_tailor.save()

        Add_order.objects.filter(id=dataid).update(length=ln, shoulder=sd, loose=lo, neck=nc,
                                                   regal=rg, cuff_length=cl, cuff_type=ct, sleeve_type=sl,
                                                   sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
                                                   cloth=cloth,
                                                   order_date=od, delivery_date=dd, tailor=new_tailor,
                                                   button_type=bt,
                                                   neck_round=ncr, wrist=wr, collar=clr, description=other)

    messages.success(request, "Customer Details Updated Successfully...!")
    return redirect(order_details)


def save_add_order(request):
    if request.method == "POST":
        # Your existing form processing logic
        id = request.POST.get('id')
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve')
        sll = request.POST.get('sleeve_length')
        nc = request.POST.get('neck')
        wr = request.POST.get('wrist')
        ncr = request.POST.get('neck_round')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('bottom2')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('cloth')
        other = request.POST.get('other')

        # Get or create the tailor instance
        tailor_instance = AddTailors.objects.get(id=tailor_id)
        works_on_delivery_date = Add_order.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        if works_on_delivery_date >= 6:
            error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
            if request.is_ajax():
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.error(request, error_message)
                return redirect('createcustomer')

        customer_instance = Customer.objects.get(id=id)
    tailor_instance.assigned_works += 1
    tailor_instance.save()

    try:
        # Generate a unique bill_number (you can customize this logic)
        random_3_digits = random.randint(0, 999)
        bill_number = f"{timezone.now().strftime('%Y%m%d')}{random_3_digits:03d}"

        # Create the customer instance
        obj = Add_order(customer_id=customer_instance, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg,
                        cuff_length=cl,
                        cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
                        order_date=od, cloth=cloth, bill_number=bill_number,
                        delivery_date=dd, tailor=tailor_instance, button_type=bt, neck_round=ncr, wrist=wr, collar=clr,
                        description=other)

        obj.save()

        messages.success(request, f"Successfully added new order: {obj.customer_id.name}")
        return redirect('add_order', dataid=obj.customer_id.id)

    except IntegrityError as e:
        # Handle IntegrityError
        return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
    except Exception as e:
        # Handle other exceptions
        return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return redirect('add_order', dataid=obj.customer_id.id)


def search_tailor(request):
    results = {'tailors': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']
        results['tailors'] = AddTailors.objects.filter(mobile_number__icontains=query)

    return render(request, 'search_tailor.html', {'results': results, 'query': query})


def tailor_work_details(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        tailors = AddTailors.objects.all()

        tailor_data = []
        for tailor in tailors:
            assigned_works = Add_order.objects.filter(
                tailor=tailor, status='assigned', order_date__range=[start_date, end_date]
            ).count()

            pending_works = Add_order.objects.filter(
                tailor=tailor, status='in_progress', order_date__range=[start_date, end_date]
            ).count()

            completed_works = Add_order.objects.filter(
                tailor=tailor, status='completed', order_date__range=[start_date, end_date]
            ).count()

            tailor_info = {
                'tailor': tailor,
                'assigned_works': assigned_works,
                'pending_works': pending_works,
                'completed_works': completed_works
            }

            tailor_data.append(tailor_info)

        context = {
            'tailor_data': tailor_data,
            'start_date': start_date,
            'end_date': end_date,
        }

        return render(request, 'tailor_details.html', context)

    return render(request, 'tailor_work.html')


def select_dates(request):
    return render(request, "tailor_work.html")


def tailor_appointments(request, delivery_date):
    # Get all tailors
    tailors = AddTailors.objects.all()

    # Initialize dictionaries to store work details for each tailor
    assigned_works = {}
    pending_works = {}
    upcoming_works = {}

    # Iterate through each tailor
    for tailor in tailors:
        # Filter customer orders for the tailor based on delivery date
        tailor_orders = Customer.objects.filter(tailor=tailor, delivery_date=delivery_date)

        # Count the number of orders in each status for the tailor
        assigned_works[tailor] = tailor_orders.filter(status='assigned').count()
        pending_works[tailor] = tailor_orders.filter(status='in_progress').count()
        upcoming_works[tailor] = tailor_orders.filter(status='assigned', delivery_date__gt=delivery_date).count()

    # Pass the results to the template
    context = {
        'delivery_date': delivery_date,
        'assigned_works': assigned_works,
        'pending_works': pending_works,
        'upcoming_works': upcoming_works,
    }

    return render(request, 'tailor_appointment.html', context)


def login(request):
    return render(request, "login.html")


def savelogin(request):
    if request.method == "POST":
        un = request.POST.get('user_name')
        pd = request.POST.get('password')
        obj = admin_login(username=un, password=pd)
        obj.save()
        return render(savelogin)


def adminlogin(request):
    if request.method == "POST":
        un = request.POST.get('user_name')
        pwd = request.POST.get('password')
        if admin_login.objects.filter(username=un, password=pwd).exists():
            request.session['user_name'] = un
            request.session['password'] = pwd
            messages.success(request, " Login Successful")
            return redirect(dashboard)
        elif reception_login.objects.filter(user_name=un, password=pwd).exists():
            reception = reception_login.objects.get(user_name=un, password=pwd)
            request.session['username'] = un
            request.session['password'] = pwd
            messages.success(request, " Login Successful")
            return redirect(reception_indexpage)
        else:
            messages.warning(request, "Please Enter Valid username and password...")
            return redirect(login)


def LogoutAdmin(req):
    del req.session['user_name']
    del req.session['password']
    messages.success(req, 'Logout successful...!')
    return redirect(login)


def LogoutReception(req):
    del req.session['username']
    del req.session['password']
    messages.success(req, 'Logout successful...!')
    return redirect(login)
