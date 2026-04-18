from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from functools import wraps

from .models import User, Product, Order, OrderItem, DeliveryPoint
from .forms import (
    LoginForm, RegisterForm, ProductForm, OrderForm,
    OrderItemFormSet, OrderStatusForm, UserForm
)


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, 'Недостаточно прав доступа')
                return redirect('catalog')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.user)
        return redirect(request.GET.get('next', 'catalog'))
    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.ROLE_CLIENT
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.full_name}!')
        return redirect('catalog')
    return render(request, 'shop/register.html', {'form': form})


def catalog_view(request):
    products = Product.objects.filter(is_active=True)
    is_auth = request.user.is_authenticated

    if is_auth:
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '')
        cake_type = request.GET.get('cake_type', '')
        bakery = request.GET.get('bakery', '')
        price_min = request.GET.get('price_min', '')
        price_max = request.GET.get('price_max', '')
        sort = request.GET.get('sort', '')

        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if category:
            products = products.filter(category__icontains=category)
        if cake_type:
            products = products.filter(cake_type__icontains=cake_type)
        if bakery:
            products = products.filter(bakery__icontains=bakery)
        if price_min:
            try:
                products = products.filter(price__gte=float(price_min))
            except ValueError:
                pass
        if price_max:
            try:
                products = products.filter(price__lte=float(price_max))
            except ValueError:
                pass

        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'name_asc': 'name',
            'name_desc': '-name',
            'discount_desc': '-discount',
        }
        if sort in sort_map:
            products = products.order_by(sort_map[sort])

        all_products = Product.objects.filter(is_active=True)
        categories = sorted(set(all_products.values_list('category', flat=True)))
        cake_types = sorted(set(all_products.values_list('cake_type', flat=True)))
        bakeries = sorted(set(all_products.values_list('bakery', flat=True)))
    else:
        search = category = cake_type = bakery = price_min = price_max = sort = ''
        categories = cake_types = bakeries = []

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    return render(request, 'shop/catalog.html', {
        'products': products_page,
        'is_auth': is_auth,
        'search': search,
        'category': category,
        'cake_type': cake_type,
        'bakery': bakery,
        'price_min': price_min,
        'price_max': price_max,
        'sort': sort,
        'categories': categories,
        'cake_types': cake_types,
        'bakeries': bakeries,
    })


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def orders_view(request):
    user = request.user
    orders = Order.objects.select_related('delivery_point', 'customer').prefetch_related('items__product')

    if user.role == User.ROLE_CLIENT:
        orders = orders.filter(customer=user)
    elif user.role in (User.ROLE_MANAGER, User.ROLE_ADMIN):
        search = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        sort = request.GET.get('sort', '-order_date')

        if search:
            orders = orders.filter(
                Q(customer_name__icontains=search) |
                Q(number__icontains=search)
            )
        if status_filter:
            orders = orders.filter(status=status_filter)
        if date_from:
            orders = orders.filter(order_date__gte=date_from)
        if date_to:
            orders = orders.filter(order_date__lte=date_to)

        sort_map = {
            '-order_date': '-order_date',
            'order_date': 'order_date',
            '-number': '-number',
            'number': 'number',
        }
        if sort in sort_map:
            orders = orders.order_by(sort_map[sort])
    else:
        orders = orders.none()

    paginator = Paginator(orders, 15)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)

    return render(request, 'shop/orders.html', {
        'orders': orders_page,
        'status_choices': Order.STATUS_CHOICES,
        'search': request.GET.get('search', ''),
        'status_filter': request.GET.get('status', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'sort': request.GET.get('sort', '-order_date'),
    })


@login_required
def order_detail_view(request, pk):
    user = request.user
    order = get_object_or_404(Order, pk=pk)

    if user.role == User.ROLE_CLIENT and order.customer != user:
        messages.error(request, 'Нет доступа к этому заказу')
        return redirect('orders')

    status_form = None
    if user.role in (User.ROLE_MANAGER, User.ROLE_ADMIN):
        status_form = OrderStatusForm(request.POST or None, instance=order)
        if request.method == 'POST' and status_form.is_valid():
            status_form.save()
            messages.success(request, 'Статус заказа обновлён')
            return redirect('order_detail', pk=pk)

    return render(request, 'shop/order_detail.html', {
        'order': order,
        'status_form': status_form,
    })


@role_required(User.ROLE_ADMIN)
def product_create_view(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Товар добавлен')
        return redirect('catalog')
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Добавить товар'})


@role_required(User.ROLE_ADMIN)
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Товар обновлён')
        return redirect('product_detail', pk=pk)
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Редактировать товар', 'product': product})


@role_required(User.ROLE_ADMIN)
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, 'Товар удалён')
        return redirect('catalog')
    return render(request, 'shop/confirm_delete.html', {
        'object': product,
        'title': f'Удалить товар «{product.name}»?',
        'back_url': 'catalog',
    })


@role_required(User.ROLE_ADMIN)
def order_create_view(request):
    form = OrderForm(request.POST or None)
    formset = OrderItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        order = form.save()
        formset.instance = order
        formset.save()
        messages.success(request, f'Заказ №{order.number} создан')
        return redirect('order_detail', pk=order.pk)
    return render(request, 'shop/order_form.html', {
        'form': form, 'formset': formset, 'title': 'Создать заказ'
    })


@role_required(User.ROLE_ADMIN)
def order_edit_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form = OrderForm(request.POST or None, instance=order)
    formset = OrderItemFormSet(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, 'Заказ обновлён')
        return redirect('order_detail', pk=pk)
    return render(request, 'shop/order_form.html', {
        'form': form, 'formset': formset, 'title': 'Редактировать заказ', 'order': order
    })


@role_required(User.ROLE_ADMIN)
def order_delete_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ удалён')
        return redirect('orders')
    return render(request, 'shop/confirm_delete.html', {
        'object': order,
        'title': f'Удалить заказ №{order.number}?',
        'back_url': 'orders',
    })


@role_required(User.ROLE_ADMIN)
def users_view(request):
    search = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '')
    users = User.objects.all().order_by('full_name')

    if search:
        users = users.filter(
            Q(full_name__icontains=search) | Q(email__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)

    paginator = Paginator(users, 15)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)

    return render(request, 'shop/users.html', {
        'users': users_page,
        'search': search,
        'role_filter': role_filter,
        'role_choices': User.ROLE_CHOICES,
    })


@role_required(User.ROLE_ADMIN)
def user_create_view(request):
    form = UserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if user.role == User.ROLE_ADMIN:
            user.is_staff = True
        user.save()
        messages.success(request, f'Пользователь {user.full_name} создан')
        return redirect('users')
    return render(request, 'shop/user_form.html', {'form': form, 'title': 'Добавить пользователя'})


@role_required(User.ROLE_ADMIN)
def user_edit_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user_obj)
    if request.method == 'POST' and form.is_valid():
        user_obj = form.save(commit=False)
        password = form.cleaned_data.get('password')
        if password:
            user_obj.set_password(password)
        user_obj.is_staff = user_obj.role == User.ROLE_ADMIN
        user_obj.save()
        messages.success(request, 'Пользователь обновлён')
        return redirect('users')
    return render(request, 'shop/user_form.html', {
        'form': form, 'title': f'Редактировать: {user_obj.full_name}', 'user_obj': user_obj
    })


@role_required(User.ROLE_ADMIN)
def user_delete_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.user.pk == user_obj.pk:
        messages.error(request, 'Нельзя удалить себя')
        return redirect('users')
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'Пользователь удалён')
        return redirect('users')
    return render(request, 'shop/confirm_delete.html', {
        'object': user_obj,
        'title': f'Удалить пользователя {user_obj.full_name}?',
        'back_url': 'users',
    })
