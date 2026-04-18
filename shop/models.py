from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CLIENT = 'client'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Авторизированный клиент'),
        (ROLE_MANAGER, 'Менеджер'),
        (ROLE_ADMIN, 'Администратор'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    @property
    def is_client(self):
        return self.role == self.ROLE_CLIENT


class DeliveryPoint(models.Model):
    address = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'
        ordering = ['address']

    def __str__(self):
        return self.address


class Product(models.Model):
    article = models.CharField(max_length=20, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    unit = models.CharField(max_length=50, default='шт.', verbose_name='Единица измерения')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (руб.)')
    bakery = models.CharField(max_length=255, verbose_name='Кондитерская / Бренд')
    cake_type = models.CharField(max_length=255, verbose_name='Тип торта')
    category = models.CharField(max_length=255, verbose_name='Категория')
    discount = models.PositiveSmallIntegerField(default=0, verbose_name='Скидка (%)')
    stock = models.PositiveIntegerField(default=0, verbose_name='Кол-во на складе')
    description = models.TextField(blank=True, verbose_name='Описание')
    photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Фото')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount:
            return self.price * (100 - self.discount) / 100
        return self.price


class Order(models.Model):
    STATUS_NEW = 'Новый'
    STATUS_IN_PROGRESS = 'В обработке'
    STATUS_READY = 'Готов к выдаче'
    STATUS_COMPLETED = 'Завершен'
    STATUS_CANCELLED = 'Отменен'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_IN_PROGRESS, 'В обработке'),
        (STATUS_READY, 'Готов к выдаче'),
        (STATUS_COMPLETED, 'Завершен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]

    number = models.PositiveIntegerField(unique=True, verbose_name='Номер заказа')
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Клиент'
    )
    customer_name = models.CharField(max_length=255, verbose_name='ФИО клиента')
    order_date = models.DateField(verbose_name='Дата заказа')
    delivery_date = models.DateField(verbose_name='Дата доставки')
    delivery_point = models.ForeignKey(
        DeliveryPoint, on_delete=models.PROTECT,
        verbose_name='Пункт выдачи'
    )
    receipt_code = models.PositiveIntegerField(verbose_name='Код для получения')
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date', '-number']

    def __str__(self):
        return f'Заказ №{self.number}'

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.product.discounted_price * self.quantity
