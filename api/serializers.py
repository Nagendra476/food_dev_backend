from rest_framework import serializers
from .models import User
from . models import Cart
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'contact', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            contact=validated_data['contact'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")
    
from rest_framework import serializers
from .models import Category,Order,OrderItem,Address

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user']


class Cartserializer(serializers.ModelSerializer):
    category=CategorySerializer(read_only=True)
    user=RegisterSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ['id','category','user','quantity','added_on']


class OrderItemserializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    total_price = serializers.SerializerMethodField()    # gives the field that reads the value which is calculated

    class Meta:
        model = OrderItem
        fields = ['id', 'category', 'quantity', 'total_price','ordered_date']

    def get_total_price(self, obj):
        return obj.total_price
    
class Orderserializer(serializers.ModelSerializer):
    user=RegisterSerializer(read_only=True)
    items = OrderItemserializer(many=True, read_only=True)
    class Meta:
        model=Order
        fields=['id','user','total','added_on','items']
#modified
from rest_framework import serializers
from .models import Order

class OrderItemSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    quantity = serializers.IntegerField()


class Addressserializer(serializers.ModelSerializer):
    class Meta:
        model=Address
        fields='__all__'
        read_only_fields = ['user']    
      
from .models import Item
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'description', 'category', 'image']
