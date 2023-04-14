from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product
# Start of mpesa related imports
from django_daraja.mpesa import utils
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime
# End of mpesa related imports

#

# Start of mpesa instances and variables
cl = MpesaClient()
STK_push_callback_url = "https://api.darajambili.com/express-payment                                                                            "
b2c_callback_url = ""
# End of mpesa instances and variables
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect("register")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def add_products(request):
    if request.method == "POST":
        p_name = request.POST.get("jina")
        p_price = request.POST.get("bei")
        p_quantity= request.POST.get("jina")
        product = Product (prod_name=p_name, prod_quantity=p_quantity,
                           prod_price=p_price)
        product.save()
        messages.success(request, 'product saved successfully!')
        return redirect('add products')
    return render(request, 'add products.html')

    return render(request, 'add products.html')

@login_required()
def view_products(request):

    products = Product.objects.all()

    return render(request, 'products.html', {'products': products})


@login_required()
def delete_product(request, id):
    # Select the product you need to delete_product
    product = Product.objects.get(id=id)
    # Finally delete the product
    product.delete()
    # Redirect back to products page with a success message
    messages.success(request, 'Product deleted successfully')
    return redirect('products')

@login_required
def update_product(request, id):
    # Select the product to be updated
    product = Product.objects.get(id=id)

    # Check if the form has any submitted records to receive then
    if request.method == "POST":
        updated_name = request.POST.get('jina')
        updated_quantity = request.POST.get('kiasi')
        updated_price = request.POST.get('bei')

        # Update the selected product above with the received data
        product.prod_name = updated_name
        product.prod_quantity = updated_quantity
        product.prod_price = updated_price
        # Return the updated data back to the database
        product.save()

        # Redirect back to the products page with a success message
        messages.success(request, 'product updated successfully')
        return redirect('products')
    return render(request, 'update-product.html', {'product': product})

def auth_success(request):
    token = cl.access_token()
    return JsonResponse(token, safe=False)


@login_required()
def payment(request, id):
    #select the product being paid
    product = Product.objects.get(id=id)
    # Check if the form being submitted has a post method
    if request.method == "POST":
        phone_number = request.POST.get('nambari')
        amount = request.POST.get('bei')
        amount = int(amount)
        #Proceed with the payment by launching M-PESA STK
        account_ref = 'WANYAMA001'
        transaction_description = 'payment for a product'
        stk = cl.stk_push(phone_number, amount, account_ref,transaction_description, stk_push_callback_url)
        mpesa_response = stk.response_description
        messages.success(request, mpesa_response)
        return redirect('pay-via-mpesa')
    return render(request, 'payment.html', {'product': product})