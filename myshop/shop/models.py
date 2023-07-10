from django.db import models
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='category_images', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Customer(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.email

    @staticmethod
    def authenticate(email, password):
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                return customer
        except ObjectDoesNotExist:
            pass
        return None


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=1)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    placed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.pk} - {self.product.name}"


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.postal_code}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.customer.email} - {self.product.name}"

# end models.py