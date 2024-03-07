from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class AddTailors(AbstractUser):
    tailor = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, unique=True, null=True)
    password = models.CharField(max_length=10, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True)
    id = models.AutoField(primary_key=True)
    assigned_works = models.IntegerField(default=0)
    pending_works = models.IntegerField(default=0)
    upcoming_works = models.IntegerField(default=0)
    completed_works = models.IntegerField(default=0)

    def __str__(self):
        return str(self.tailor)
  # Convert to string before returning

class Customer(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=False)
    length = models.CharField(max_length=15)
    shoulder = models.CharField(max_length=15)
    cloth = models.CharField(max_length=20, null=True)
    SLEEVE_CHOICES = [
        ('half_sleeve', 'Half Sleeve'),
        ('full_sleeve', 'Full Sleeve'),
    ]
    sleeve_type = models.CharField(
        max_length=15,
        choices=SLEEVE_CHOICES,
        default='half_sleeve',
    )

    sleeve_length = models.CharField(max_length=15)
    neck = models.CharField(max_length=15)
    neck_round = models.CharField(max_length=15,null=True)
    collar = models.CharField(max_length=15,null=True)
    regal = models.CharField(max_length=15)
    loose = models.CharField(max_length=15)
    wrist = models.CharField(max_length=15,null=True)
    pocket = models.CharField(max_length=15)

    CUFF_CHOICES = [
        ('cuff', 'Cuff'),
        ('normal', 'Normal'),
    ]
    cuff_type = models.CharField(
        max_length=10,
        choices=CUFF_CHOICES,
        default='normal',
    )

    cuff_length = models.CharField(max_length=15)
    bottom1 = models.CharField(max_length=50)
    bottom2 = models.CharField(max_length=50)

    BUTTON_CHOICES = [
        ('bayyin_mahfi', 'Bayyin Mahfi'),
        ('zip_mahfi', 'Zip Mahfi'),
        ('mahfi', 'Mahfi'),
        ('button_bayyin', 'Button Bayyin'),
    ]
    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
    )

    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    tailor = models.ForeignKey(AddTailors, on_delete=models.SET_NULL, null=True)
       
    description = models.CharField(blank=True, null=True,max_length=100000)
    history = models.TextField(blank=True, null=True)
    bill_number = models.CharField(max_length=15,null=True)
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        # Add more status choices if needed
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
    )

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    details = models.TextField()
    order_date = models.DateField()
    delivery_date = models.DateField()

    def __str__(self):
        return f"Order for {self.customer.name} - {self.order_date}"



class reception_login(models.Model):
    user_name = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20,null=True)

class admin_login(models.Model):
    username = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20,null=True)


class Add_order(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    length = models.CharField(max_length=15)
    shoulder = models.CharField(max_length=15)
    cloth = models.CharField(max_length=20, null=True)
    SLEEVE_CHOICES = [
        ('half_sleeve', 'Half Sleeve'),
        ('full_sleeve', 'Full Sleeve'),
    ]
    sleeve_type = models.CharField(
        max_length=15,
        choices=SLEEVE_CHOICES,
        default='half_sleeve',
    )

    sleeve_length = models.CharField(max_length=15)
    neck = models.CharField(max_length=15)
    neck_round = models.CharField(max_length=15, null=True)
    collar = models.CharField(max_length=15, null=True)
    regal = models.CharField(max_length=15)
    loose = models.CharField(max_length=15)
    wrist = models.CharField(max_length=15, null=True)
    pocket = models.CharField(max_length=15)

    CUFF_CHOICES = [
        ('cuff', 'Cuff'),
        ('normal', 'Normal'),
    ]
    cuff_type = models.CharField(
        max_length=10,
        choices=CUFF_CHOICES,
        default='normal',
    )

    cuff_length = models.CharField(max_length=15)
    bottom1 = models.CharField(max_length=50)
    bottom2 = models.CharField(max_length=50)

    BUTTON_CHOICES = [
        ('bayyin_mahfi', 'Bayyin Mahfi'),
        ('zip_mahfi', 'Zip Mahfi'),
        ('mahfi', 'Mahfi'),
        ('button_bayyin', 'Button Bayyin'),
    ]
    button_type = models.CharField(
        max_length=15,
        choices=BUTTON_CHOICES,
    )

    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    tailor = models.ForeignKey(AddTailors, on_delete=models.SET_NULL, null=True)

    description = models.CharField(blank=True, null=True, max_length=100000)
    history = models.TextField(blank=True, null=True)
    bill_number = models.CharField(max_length=15, null=True)
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        # Add more status choices if needed
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
    )


class Item(models.Model):
    order_id = models.ForeignKey(Add_order, on_delete=models.CASCADE,null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    item_name = models.CharField(max_length=100, null=True)
    item_quantity = models.PositiveIntegerField(null=True)
    item_price = models.FloatField(null=True)
    total_price = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        # Calculate total price before saving
        self.total_price = self.item_quantity * self.item_price
        super().save(*args, **kwargs)