# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Product, Order, Category, Cart, Address
from .forms import CustomerRegistrationForm, AddressForm
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.contrib import messages

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            name = form.cleaned_data['name']

            if password1 != password2:
                form.add_error('password2', 'Passwords you entered do not match')
            else:
                hashed_password = make_password(password1)
                customer = Customer(email=email, password=hashed_password, name=name)
                customer.save()
                return redirect('shop:customer_login')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'shop/register.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        customer = Customer.authenticate(email=email, password=password)
        if customer is not None:
            request.session['customer_id'] = customer.id
            return redirect('shop:products_list')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid email or password'})
    else:
        return render(request, 'shop/login.html')

def customers_list(request):
    customers = Customer.objects.all()
    return render(request, 'shop/customers_list.html', {'customers': customers})

def products_list(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    if selected_category_id != '':
        products = Product.objects.filter(is_active=True, category__id=selected_category_id)
    else:
        products = Product.objects.filter(is_active=True)

    if search_query != '':
        products = products.filter(name__icontains=search_query)

    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    customer_id = request.session.get('customer_id')
    return render(request, 'shop/product_list.html', {'categories': categories, 'products': page_obj, 'customer_id': customer_id, 'selected_category_id': selected_category_id, 'search_query': search_query})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer_id = request.session.get('customer_id')
    return render(request, 'shop/product_detail.html', {'product': product, 'customer_id': customer_id})

def add_to_cart(request, product_id):
    if not request.session.get('customer_id'):
        return redirect('shop:customer_login')

    customer_id = request.session['customer_id']
    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    # Check if the product is already in the cart for the customer
    cart_item = Cart.objects.filter(customer=customer, product=product).first()

    if cart_item:
        messages.warning(request, 'Product is already in the cart.')
    else:
        # Product is not in the cart, create a new cart item
        cart_item = Cart(customer=customer, product=product)
        cart_item.save()
        messages.success(request, 'Product added to cart.')

    return redirect('shop:cart')

def cart(request):
    customer_id = request.session.get('customer_id')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        cart_items = Cart.objects.filter(customer=customer)
        cart_total = sum(item.product.price for item in cart_items)
    else:
        cart_items = []
        cart_total = 0

    return render(request, 'shop/cart.html', {'customer_id': customer_id, 'cart_items': cart_items, 'cart_total': cart_total})

def remove_from_cart(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        product_id = request.POST.get('product_id')

        if customer_id and product_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                product = Product.objects.get(id=product_id)
                cart_item = Cart.objects.get(customer=customer, product=product)
                cart_item.delete()
                messages.success(request, 'Product removed from cart.')
            except (Customer.DoesNotExist, Product.DoesNotExist, Cart.DoesNotExist):
                messages.error(request, 'An error occurred while removing the product from cart.')
        else:
            messages.error(request, 'Invalid request.')

    return redirect('shop:cart')

def order_status(request):
    customer_id = request.session.get('customer_id')
    if customer_id:
        orders = Order.objects.filter(customer_id=customer_id)
        return render(request, 'shop/order_status.html', {'orders': orders, 'customer_id': customer_id})
    else:
        messages.error(request, 'You need to be logged in to view your order status.')
        return redirect('shop:customer_login')

def customer_logout(request):
    # Remove the authenticated customer from the session
    del request.session['customer_id']
    return redirect('shop:products_list')

def address_selection(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)
    addresses = Address.objects.filter(customer=customer)
    selected_address_id = request.GET.get('address', '')

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address_line1 = form.cleaned_data['address_line1']
            address_line2 = form.cleaned_data['address_line2']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            postal_code = form.cleaned_data['postal_code']

            if selected_address_id:
                address = get_object_or_404(Address, id=selected_address_id)
                address.address_line1 = address_line1
                address.address_line2 = address_line2
                address.city = city
                address.state = state
                address.postal_code = postal_code
                address.save()
            else:
                address = Address(customer=customer, address_line1=address_line1, address_line2=address_line2, city=city, state=state, postal_code=postal_code)
                address.save()

            messages.success(request, 'Address updated successfully.')
            return redirect('shop:address_selection')
    else:
        form = AddressForm()

        if selected_address_id:
            address = get_object_or_404(Address, id=selected_address_id)
            form.fields['address_line1'].initial = address.address_line1
            form.fields['address_line2'].initial = address.address_line2
            form.fields['city'].initial = address.city
            form.fields['state'].initial = address.state
            form.fields['postal_code'].initial = address.postal_code

    return render(request, 'shop/address_selection.html', {'customer_id': customer_id, 'addresses': addresses, 'selected_address_id': selected_address_id, 'form': form})

def place_order(request):
    customer_id = request.session.get('customer_id')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
        cart_items = Cart.objects.filter(customer=customer)

        # Create orders for each cart item
        for cart_item in cart_items:
            Order.objects.create(
                customer=customer,
                product=cart_item.product,
                status='approved'
            )

        # Clear the cart for the customer
        cart_items.delete()

        # Display order confirmation
        messages.success(request, 'Order placed successfully!')
    else:
        messages.error(request, 'You need to be logged in to place an order.')

    return redirect('shop:order_confirmation')

def order_confirmation(request):
    customer_id = request.session.get('customer_id')
    return render(request, 'shop/order_confirmation.html', {"customer_id": customer_id})

def index(request):
    return redirect('shop:products_list')
    
# end views.py