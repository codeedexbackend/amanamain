# models.py

from django.db import models
from django.utils import timezone
from .utils import generate_bill_number

class AddTailor(models.Model):
    tailor = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(max_length=10, null=True)
    mobile_number = models.CharField(max_length=15,unique=True,null=True)

    def __str__(self):
        return self.tailor
    

class AddCustomer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, default='1')
    tailor = models.ForeignKey(AddTailor, on_delete=models.SET_NULL, null=True, blank=True)
    length = models.CharField(max_length=15, default='1')
    shoulder = models.CharField(max_length=15, default='1')
    loose = models.CharField(max_length=15, default='1')
    neck = models.CharField(max_length=15, default='1')
    regal = models.CharField(max_length=15, default='1')
    cuf = models.CharField(max_length=15, default='1')
    pocket_size = models.CharField(max_length=15,null=True,blank=True)

    CUF_CHOICES = [
        ('cuff', 'Cuff'),
        ('normal', 'Normal'),
    ]

    cuftype = models.CharField(
        max_length=10,
        choices=CUF_CHOICES,
        default='normal',
    )
    sleeve = models.CharField(max_length=15, default='1')

    SLEEVE_CHOICES = [
        ('half_sleeve', 'Half Sleeve'),
        ('full_sleeve', 'Full Sleeve'),
    ]

    sleeve_type = models.CharField(
        max_length=15,
        choices=SLEEVE_CHOICES,
        default='half_sleeve',
    )

    bill_number = models.CharField(max_length=50, unique=True, editable=False)
    order_date = models.DateField(null=True, default=timezone.now)
    delivery_date = models.DateField(null=True)
    bottom1 = models.CharField(max_length=50, blank=True, null=True, default='1')
    bottom2 = models.CharField(max_length=50, blank=True, null=True, default='1')

    BUTTON_CHOICES = [
        ('bayyin_mahfi', 'Bayyin Mahfi'),
        ('zip_mahfi', 'Zip Mahfi'),
        ('button_bayyin', 'Button Bayyin'),
    ]

    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate the bill number if it doesn't exist
            self.bill_number = self.generate_bill_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} - {self.bill_number}"

    def get_printable_measurement(self):
        return f"Customer: {self.name}\nTailor: {self.tailor if self.tailor else 'Not assigned'}\n"\
               f"Length: {self.length}, Shoulder: {self.shoulder}, Loose: {self.loose}, Neck: {self.neck}, "\
               f"Regal: {self.regal}, Cuff: {self.cuf}, Sleeve: {self.sleeve}, Sleeve Type: {self.get_sleeve_type_display()}\n"\
               f"Order Date: {self.order_date}, Delivery Date: {self.delivery_date}\n"\
               f"Bottom 1: {self.bottom1}, Bottom 2: {self.bottom2}, Button Type: {self.get_button_type_display()}"

    def generate_bill_number(self):
        # Get the current year and month
        year_month = timezone.now().strftime('%Y%m')

        # Count existing orders with the same year and month
        existing_orders_count = AddCustomer.objects.filter(bill_number__startswith=f'AMANA-{year_month}-').count()

        # Format the bill number with the prefix and counter
        return f'AMANA-{year_month}-{existing_orders_count + 1:03d}'


class WorkStatus(models.Model):
    customer = models.ForeignKey(AddCustomer, on_delete=models.CASCADE)
    tailor = models.ForeignKey(AddTailor, on_delete=models.CASCADE)
    status_choices = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)

    def __str__(self):
        return f"{self.customer.name} - {self.status}"


class Order(models.Model):
    customer = models.ForeignKey(AddCustomer, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    tailor = models.ForeignKey(AddTailor, on_delete=models.SET_NULL, null=True, blank=True)


