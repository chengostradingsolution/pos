from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from flask import jsonify
from posApp.models import Category, Products, Sales, salesItems,CartItem,Customer
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
import datetime
from twilio.rest import Client
from .utils import amount_in_words,generate_invoice_number


from datetime import date, datetime

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    transaction = len(Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total',flat=True))
    context = {
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
    }
    return render(request, 'posApp/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)
@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)

@login_required
def save_product(request):
    data =  request.POST
    resp = {'status':'failed'}
    id= ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
    if len(check) > 0 :
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_product = Products.objects.filter(id = data['id']).update(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'],uom = data['uom'],cgst = data['cgst'],sgst = data['sgst'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


# Customers
@login_required
def customers(request):
    customer_list = Customer.objects.all()
    context = {
        'page_title':'Customer List',
        'customers':customer_list,
    }
    return render(request, 'posApp/customers.html',context)

@login_required
def manage_customers(request):
    customer = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            customer = Customer.objects.filter(id=id).first()
    
    context = {
        'customer' : customer,
        'categories' : categories
    }
    return render(request, 'posApp/manage_customer.html',context)

# @login_required
# def save_customer(request):
#     data =  request.POST
#     resp = {'status':'failed'}
#     id= ''
#     if 'id' in data:
#         id = data['id']
#     if id.isnumeric() and int(id) > 0:
#         check = Customer.objects.exclude(id=id).filter(gstin=data['gstin']).all()
#     else:
#         check = Customer.objects.filter(gstin=data['gstin']).all()
#     if len(check) > 0 :
#         resp['msg'] = "Customer Already Exists in the database"
#     else:
#         try:
#             if (data['id']).isnumeric() and int(data['id']) > 0 :
#                 save_customer = Customer.objects.filter(id = data['id']).update(name = data['name'],phone = data['phone'],address = data['address'],city = data['city'],state = data['state'],pin = data['pin'],statecode = data['statecode'],email = data['email'],gstin = data['gstin'],status = data['status'])
#             else:
#                 save_customer=Customer(name = data['name'],phone = data['phone'],address = data['address'],city = data['city'],state = data['state'],pin = data['pin'],statecode = data['statecode'],email = data['email'],gstin = data['gstin'],status = data['status'],)
#                 save_customer.save()
#                 print(save_customer)
#             resp['status'] = 'success'
#             messages.success(request, 'Customer Successfully saved.')
#         except:
#             resp['status'] = 'failed'
#     return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def save_customer(request):
    data = request.POST
    print(request.POST)
    resp = {'status': 'failed'}

    id = data.get('id', '').strip()   # ✅ SAFE access

    if id.isnumeric() and int(id) > 0:
        check = Customer.objects.exclude(id=id).filter(gstin=data['gstin'])
    else:
        check = Customer.objects.filter(gstin=data['gstin'])

    if check.exists():
        resp['msg'] = "Customer Already Exists in the database"
        return HttpResponse(json.dumps(resp), content_type="application/json")

    try:
        if id.isnumeric() and int(id) > 0:
            Customer.objects.filter(id=id).update(
                name=data['name'],
                phone=data['phone'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                pin=data['pin'],
                statecode=data['statecode'],
                email=data['email'],
                gstin=data['gstin'],
                
                sname=data['ship_name'],
                sphone=data['ship_phone'],
                saddress=data['ship_address'],
                scity=data['ship_city'],
                sstate=data['ship_state'],
                spin=data['ship_pin'],
                sstatecode=data['ship_statecode'],
                semail=data['ship_email'],
                sgstin=data['ship_gstin'],
                
                status=data['status']
            )
        else:
            Customer.objects.create(
                name=data['name'],
                phone=data['phone'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                pin=data['pin'],
                statecode=data['statecode'],
                email=data['email'],
                gstin=data['gstin'],
                
                
                sname=data['ship_name'],
                sphone=data['ship_phone'],
                saddress=data['ship_address'],
                scity=data['ship_city'],
                sstate=data['ship_state'],
                spin=data['ship_pin'],
                sstatecode=data['ship_statecode'],
                semail=data['ship_email'],
                sgstin=data['ship_gstin'],
                
                status=data['status']
            )

        resp['status'] = 'success'
        messages.success(request, 'Customer Successfully saved.')

    except Exception as e:
        resp['status'] = 'failed'
        resp['error'] = str(e)   # ✅ see real error in response

    return HttpResponse(json.dumps(resp), content_type="application/json")







@login_required
def delete_customer(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Customer.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Customer Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")






def test(request):
    categories = Category.objects.all()

    g=salesItems.objects.get(id=66)
    context = {
        'categories' : categories,
        'g':g
    }
    return render(request, 'posApp/test.html',context)


@login_required
def pos(request):
    r=request.user
    products = Products.objects.filter(status = 1)
    product_json = []
    if 'cart_item_ids' not in request.session:
        request.session['cart_item_ids'] = []
   
    cart_item_ids = request.session.get('cart_item_ids', [])
    cartitems = CartItem.objects.filter(id__in=cart_item_ids)


    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json),
        'r':r,
        'cartitems':cartitems,
    }
    
    # return HttpResponse('')
    return render(request, 'posApp/pos3.html',context)








def addproductpos(request,id):
    r=request.user
    product = Products.objects.get(id=id)
    if request.method=='POST':
        username=r
        # sale_id = 
        name =product.name 
        code = product.code

        uom=product.uom
        qty = request.POST['product_qty']

        
        price = request.POST['product_price']
        tamount = request.POST['product_total']
        dispercent=request.POST['product_dispercent']
        dis=request.POST['product_dis']

        taxamount = request.POST['product_taxamount']

        sgstpercent=request.POST['product_sgstpercent']

        sgst=request.POST['product_sgst']
    
        cgstpercent=request.POST['product_cgstpercent']

        cgst=request.POST['product_cgst']
        totalamount = request.POST['product_totalamount']
        c=CartItem(username=username,name=name,code=code,uom=uom,qty=qty,price=price,tamount=tamount,dispercent=dispercent,dis=dis,taxamount=taxamount,sgst=sgst,sgstpercent=sgstpercent,cgstpercent=cgstpercent,cgst=cgst,totalamount=totalamount)
        c.save()
        l=request.session["cart_item_ids"]
        l.append(c.id)
        request.session["cart_item_ids"] = l
        
       
        return redirect('/pos/')
    
@login_required
def deleteproductpos(request, id):
    cart_item_ids = request.session.get('cart_item_ids', [])

    if id in cart_item_ids:
        CartItem.objects.filter(id=id).delete()
        cart_item_ids.remove(id)
        request.session['cart_item_ids'] = cart_item_ids

    return redirect('/pos/')


@login_required
def deleteproductposflash(request):
    cart_item_ids = request.session.get('cart_item_ids', [])

    if cart_item_ids:
        CartItem.objects.filter(id__in=cart_item_ids).delete()

    # Clear session cart
    request.session['cart_item_ids'] = []

    return redirect('/')



    
@login_required
def checkpage(request):
    r=request.user
    products = Products.objects.filter(status = 1)
    cusomers=Customer.objects.all()
    product_json = []
    if 'cart_item_ids' not in request.session:
        request.session['cart_item_ids'] = []
   
    cart_item_ids = request.session.get('cart_item_ids', [])
    cartitems = CartItem.objects.filter(id__in=cart_item_ids)


    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json),
        'r':r,
        'cartitems':cartitems,
        'customers':cusomers,
    }
    
    # return HttpResponse('')
    return render(request, 'posApp/checkpage.html',context)






@login_required
def checkpageaddcustomer(request):
    if request.method=='POST':
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']

        state = request.POST['state']
        pin = request.POST['pin']
        statecode = request.POST['statecode']


        email = request.POST['email']
        gstin = request.POST['gstin']
        sname = request.POST['sname']
        sphone = request.POST['sphone']
        saddress = request.POST['saddress']
        scity = request.POST['scity']

        sstate = request.POST['sstate']
        spin = request.POST['spin']
        sstatecode = request.POST['sstatecode']


        semail = request.POST['semail']
        sgstin = request.POST['sgstin']
        c1=Customer(name = name,phone = phone,address = address,city = city,state = state,pin = pin,statecode = statecode,email = email,gstin = gstin,status = 1,sname = sname,sphone = sphone,saddress = saddress,scity = scity,sstate = sstate,spin = spin,sstatecode = sstatecode,semail = semail,sgstin = sgstin)
        c1.save()
        
        
        
        return redirect('/checkpage/')


@login_required
def createsale(request,custid):
    if request.method=='POST':
        user_id=request.user
        code = generate_invoice_number()
        customer_id = custid
        subtotal = request.POST['sub_total1']
        grandtotal = request.POST['grand_total1']

        taxamount = request.POST['taxamount1']
        totaldiscounts = request.POST['total_discount1']
        print(subtotal)
        print(taxamount)
        print(totaldiscounts)
        print(grandtotal)
        s1=Sales(user_id=user_id,code=code,customer_id=customer_id,sub_total=subtotal,grand_total=grandtotal,tax_amount=taxamount,total_discounts=totaldiscounts)
        s1.save()
        cart_item_ids = request.session.get('cart_item_ids', [])
        c1 = CartItem.objects.filter(id__in=cart_item_ids)

        tqty=0
        tcgst=0
        tsgst=0
        for item in c1:
            item.sale_id=s1.code
            item.customer_id=customer_id
            item.save()
            tqty=tqty+item.qty
            tcgst=tcgst+item.cgst
            tsgst=tsgst+item.sgst
            
        s1.tqty=tqty
        s1.tcgst=tcgst
        s1.tsgst=tsgst
        s1.ttax=tcgst+tsgst
        s1.taxable=int(subtotal)-int(totaldiscounts)
        s1.save()
        cu1=Customer.objects.get(id=customer_id)
        grand_total_words = amount_in_words(float(grandtotal))
        grand_total_words=grand_total_words.upper()

        context={
            'sale':s1,
            'cartitems':c1,
            'customer':cu1,
            'grand_total_words':grand_total_words,
            
        }
        request.session['cart_item_ids'] = []

        
        return render(request,"posApp/invoice_page.html",context)







@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status':'failed','msg':''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code = str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        sales = Sales(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change =data['amount_change']).save()
        sale_id = Sales.objects.last().pk
        i = 0
        t={}
        for prod in data.getlist('product_id[]'):
            product_id = prod 
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i] 
            price = data.getlist('price[]')[i] 
            total = float(qty) * float(price)
            t.update({product:(f"Price{price}   Q={qty} total={total}")})
            print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
            salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            i += int(1)
        resp['status'] = 'success'
        resp['sale_id'] = sale_id

        # b=f'''Invoice No:
        #         From: Grozz
        #         To: Naseer
        #         Date: {datetime.datetime.now()}
        #         Products:{t}
                


        #         Total Amount Paid: {data['grand_total']}

        #         Staff:{request.user.id}-{request.user}
        #         ''',
        
        # account_sid = 'AC83f74fdbefb8d0ef569db4a94ec386ee'
        # auth_token = '33d2b1651e514e51118ee4c2b7a8e2a5'
        # client = Client(account_sid, auth_token)

        # message = client.messages.create(
        # from_='+17069178719',
        # body=t,
        
        # to='+917034859573'
        # )

        # print(message.sid)


        # m = client.messages.create(
        # from_='+17069178719',
        # body="Invoice No:"
        #         # ----------------------------------------------
        #         # From: Grozz
        #         # To: Naseer
        #         # Date: {datetime.datetime.now()}
        #         # Products:{t}
                


        #         # Total Amount Paid: {data['grand_total']}

        #         # Staff:{request.user.id}-{request.user}
        #         # ",
        # to='+917034859573'
        # )


        # print(m.sid)
        messages.success(request, "Sale Record has been saved.")
        return render(request,"invoice_page.html")
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp),content_type="application/json")



@login_required
def invoicepage(request,id):
    sale=Sales.objects.get(id=id)
    
    c1 = CartItem.objects.filter(sale_id=sale.code)
    grand_total=sale.grand_total

  
            
 
    cu1=Customer.objects.get(id=sale.customer_id)
    grand_total_words = amount_in_words(float(grand_total))
    grand_total_words=grand_total_words.upper()

    context={
            'cartitems':c1,
            'customer':cu1,
            'grand_total_words':grand_total_words,
            
    
        'sale':sale,
    }
  

    return render(request, 'posApp/invoice_page.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        # transaction['tax_amount'] = format(float(transaction['tax_amount']))
        transaction['tax_amount'] = float("{:.2f}".format(transaction['tax_amount']))

    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "transactionchange" : transaction["amount_change"],

        "salesItems" : ItemList
    }

    return render(request, 'posApp/receipt2.html',context)
    # return HttpResponse('')

@login_required
def salesList(request):
    sales = Sales.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html',context)



@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')
