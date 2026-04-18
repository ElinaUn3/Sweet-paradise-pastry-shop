from django import forms
from django.contrib.auth import authenticate
from .models import User, Product, Order, OrderItem, DeliveryPoint


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            self.user = authenticate(username=email, password=password)
            if not self.user:
                raise forms.ValidationError('Неверный email или пароль')
        return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['article', 'name', 'unit', 'price', 'bakery', 'cake_type', 'category',
                  'discount', 'stock', 'description', 'photo', 'is_active']
        widgets = {
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bakery': forms.TextInput(attrs={'class': 'form-control'}),
            'cake_type': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'article': 'Артикул',
            'name': 'Наименование',
            'unit': 'Единица измерения',
            'price': 'Цена (руб.)',
            'bakery': 'Кондитерская / Бренд',
            'cake_type': 'Тип торта',
            'category': 'Категория',
            'discount': 'Скидка (%)',
            'stock': 'Кол-во на складе',
            'description': 'Описание',
            'photo': 'Фото',
            'is_active': 'Активен',
        }


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem,
    fields=['product', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    },
    labels={
        'product': 'Товар',
        'quantity': 'Количество',
    }
)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['number', 'customer_name', 'customer', 'order_date', 'delivery_date',
                  'delivery_point', 'receipt_code', 'status']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_point': forms.Select(attrs={'class': 'form-control'}),
            'receipt_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'number': 'Номер заказа',
            'customer_name': 'ФИО клиента',
            'customer': 'Клиент (аккаунт)',
            'order_date': 'Дата заказа',
            'delivery_date': 'Дата доставки',
            'delivery_point': 'Пункт выдачи',
            'receipt_code': 'Код для получения',
            'status': 'Статус',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].required = False
        self.fields['customer'].queryset = User.objects.filter(role=User.ROLE_CLIENT)


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Статус заказа',
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Новый пароль',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Оставьте пустым, чтобы не менять'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'role': 'Роль',
            'is_active': 'Активен',
        }
