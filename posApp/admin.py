from django.contrib import admin
from posApp.models import CartItem,Category, Products, Sales, salesItems,Customer




class CartItemAdmin(admin.ModelAdmin):
    list_display=[ 'id','username','sale_id','name','code','uom','qty','price','tamount', 'dispercent','dis','taxamount','sgstpercent','sgst',"cgstpercent","cgst","totalamount",
]

class CustomerAdmin(admin.ModelAdmin):
    list_display=[ 'id','name','gstin','phone','email','city','state','date_added'
]   
    
    
# Register your models here.
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Sales)
admin.site.register(salesItems)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Customer,CustomerAdmin)

# admin.site.register(Employees)
