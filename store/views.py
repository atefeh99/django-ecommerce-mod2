from django.shortcuts import render
from . models import *
from django.http import JsonResponse
import datetime
import json
from .utils import cookieCart, cartData, guestOrder


# Create your views here.


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

       
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

        
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'store/checkout.html', context)


def UpdateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('ProductId:', productId)

    product = Product.objects.get(id=productId)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(
        product=product, order=order)

    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)

    order_item.save()
    if order_item.quantity <= 0:
        order_item.delete()
    # when u want to return a non dictionary response you should set 'safe' attribute to false
    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data= json.loads(request.body)
    if request.user.is_authenticated: 
        customer = request.user.customer
        order, created = Order.objects.get_or_create(complete=False, customer=customer)
        
    else:
        customer, order = guestOrder(request, data)
        print ('order and customer')
    
    total= float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']

        )

    return JsonResponse('Payment complete!', safe=False)
