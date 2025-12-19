from datetime import datetime
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# class Employees(models.Model):
#     code = models.CharField(max_length=100,blank=True) 
#     firstname = models.TextField() 
#     middlename = models.TextField(blank=True,null= True) 
#     lastname = models.TextField() 
#     gender = models.TextField(blank=True,null= True) 
#     dob = models.DateField(blank=True,null= True) 
#     contact = models.TextField() 
#     address = models.TextField() 
#     email = models.TextField() 
#     department_id = models.ForeignKey(Department, on_delete=models.CASCADE) 
#     position_id = models.ForeignKey(Position, on_delete=models.CASCADE) 
#     date_hired = models.DateField() 
#     salary = models.FloatField(default=0) 
#     status = models.IntegerField() 
#     date_added = models.DateTimeField(default=timezone.now) 
#     date_updated = models.DateTimeField(auto_now=True) 

    # def __str__(self):
    #     return self.firstname + ' ' +self.middlename + ' '+self.lastname + ' '
class Category(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name

class Products(models.Model):
    code = models.CharField(max_length=100)
    uom=models.CharField(max_length=100)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()
    price = models.FloatField(default=0)
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    sgst=models.FloatField(default=0)
    cgst=models.FloatField(default=0)
    dispercent=models.FloatField(default=0)



    def __str__(self):
        return self.code + " - " + self.name




    
    
    

class CartItem(models.Model):
    username=models.CharField(max_length=100)
    sale_id = models.CharField(max_length=100)
    customer_id=models.CharField(max_length=100,blank=True)
    name = models.TextField()
    code = models.CharField(max_length=100)

    uom=models.CharField(max_length=100,blank=True)
    qty = models.FloatField(default=0)

    
    price = models.FloatField(default=0)
    tamount = models.FloatField(default=0)
    dispercent=models.FloatField(default=0)
    dis=models.FloatField(default=0)

    taxamount = models.FloatField(default=0)

    sgstpercent=models.FloatField(default=0)

    sgst=models.FloatField(default=0)
   
    cgstpercent=models.FloatField(default=0)

    cgst=models.FloatField(default=0)
    totalamount = models.FloatField(default=0)



    
class Customer(models.Model):
    # code = models.CharField(max_length=100,blank=True) 
    name = models.TextField() 
    phone = models.TextField() 
    address = models.TextField() 
    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)
    pin = models.IntegerField() 
    statecode = models.IntegerField() 
    email = models.TextField() 
    gstin = models.CharField(max_length=100)
    
    sname = models.TextField() 
    sphone = models.TextField() 
    saddress = models.TextField(blank=True) 
    scity = models.CharField(max_length=100)
    sstate = models.CharField(max_length=100)
    spin = models.IntegerField(null=True, blank=True) 
    sstatecode = models.IntegerField(null=True, blank=True) 
    semail = models.TextField() 
    sgstin = models.CharField(max_length=100)
    status = models.IntegerField() 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 
    
    
    
    
class Sales(models.Model):
    user_id=models.ForeignKey(User, on_delete=models.CASCADE)
    tqty=models.IntegerField(default=0)
    code = models.CharField(max_length=100)
    customer_id=models.CharField(max_length=100,null=True)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    total_discounts = models.FloatField(default=0)
    tcgst=models.FloatField(default=0)
    tsgst=models.FloatField(default=0)
    ttax=models.FloatField(default=0)
    taxable=models.FloatField(default=0)


 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.code
    
    
    
    
class salesItems(models.Model):
    sale_id = models.ForeignKey(Sales,on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products,on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)


# class Receipt(models.Model):
#     sale_id = models.ForeignKey(Sales,on_delete=models.CASCADE)

    