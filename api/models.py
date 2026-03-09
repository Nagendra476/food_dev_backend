from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, contact, password=None):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, contact=contact)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, contact, password=None):
        user = self.create_user(email, full_name, contact, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'contact']

    def __str__(self):
        return self.email
    
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    img = models.ImageField(upload_to='categories/')  

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  
    added_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'category')
        ordering = ['-added_on']

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    total=models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * float(self.category.price)


from django.contrib.auth import get_user_model
User=get_user_model()
class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="Address")
    full_name = models.CharField(max_length=100)  
    phone_number = models.CharField(max_length=15)
    
    house_no = models.CharField(max_length=100) 
    street = models.CharField(max_length=200, blank=True, null=True)
    landmark = models.CharField(max_length=200, blank=True, null=True) 
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")

    address_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home'),
            ('work', 'Work'),
            ('other', 'Other'),
        ],
        default='home'
    )
    
    is_default = models.BooleanField(default=False)  # default address toggle
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.address_type})"

    


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    def __str__(self):
        return self.name
