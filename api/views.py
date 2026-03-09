import json
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User, Category, Cart, Order, OrderItem, Address
from .serializers import RegisterSerializer, CategorySerializer, Cartserializer, Orderserializer, Addressserializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter

# ---------------------- USER AUTH ----------------------

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user_obj = serializer.save()
        token, created = Token.objects.get_or_create(user=user_obj)  # Create token
        return Response({
            "message": "User registered successfully!",
            "token": token.key,
            "user": {
                "id": user_obj.id,
                "email": user_obj.email,
                "full_name": user_obj.full_name,
                "contact": user_obj.contact,
                "is_superuser": user_obj.is_superuser,
                "is_staff": user_obj.is_staff
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)

    if user is not None:
        # Delete old token and create a new one
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful!",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "contact": user.contact,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff
            }
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        request.user.auth_token.delete()
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid request or already logged out."}, status=status.HTTP_400_BAD_REQUEST)

# ---------------------- CART ----------------------

class Getcart(generics.ListCreateAPIView):
    serializer_class = Cartserializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        category_id = self.request.data.get('category')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValidationError({'category': 'Invalid category ID'})

        existing_item = Cart.objects.filter(user=user, category=category).first()
        if existing_item:
            existing_item.quantity += 1
            existing_item.save()
            return existing_item

        serializer.save(user=user, category=category)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart(request, pk):
    try:
        cart_item = Cart.objects.get(id=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    new_qty = request.data.get("quantity")
    if not new_qty or int(new_qty) < 1:
        return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.quantity = int(new_qty)
    cart_item.save()
    serializer = Cartserializer(cart_item)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):
    try:
        cart_item = Cart.objects.get(id=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    cart_item.delete()
    return Response({"message": "Item removed successfully."}, status=status.HTTP_204_NO_CONTENT)

# ---------------------- ORDERS ----------------------

class Orderitem(generics.ListCreateAPIView):
    serializer_class = Orderserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-added_on')

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")

        total = sum(float(item.category.price) * item.quantity for item in cart_items)
        order = serializer.save(user=user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                category=item.category,
                quantity=item.quantity
            )

        cart_items.delete()
        return order

class Orderitems1(generics.ListCreateAPIView):
    serializer_class = Orderserializer
    permission_classes = []  # No authentication required

    def get_queryset(self):
        return Order.objects.all().order_by('-added_on')

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")

        total = sum(float(item.category.price) * item.quantity for item in cart_items)
        order = serializer.save(user=user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                category=item.category,
                quantity=item.quantity
            )

        cart_items.delete()
        return order

# ---------------------- ADDRESSES ----------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer = Addressserializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_addresses(request):
    addresses = Address.objects.filter(user=request.user).order_by('-created_at')
    serializer = Addressserializer(addresses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ---------------------- CATEGORIES ----------------------

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

# ---------------------- PROFITS ----------------------

class DaywiseProfits(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        profits = (
            Order.objects.annotate(day=TruncDate('added_on'))
            .values('day')
            .annotate(total_sum=Sum('total'))
            .order_by('day')
        )
        return Response(profits)
    


#modifed 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from django.db.models import Sum
from .models import OrderItem
from .serializers import OrderItemserializer

@api_view(["GET"])
def orders_by_day(request, day):
    try:
        orders = Order.objects.filter(added_on__date=day)
        order_items = OrderItem.objects.filter(order__in=orders)

        # Build summary
        summary = {}
        for item in order_items:
            name = item.category.name
            summary[name] = summary.get(name, 0) + item.quantity

        pie_chart = [{"name": k, "quantity": v} for k, v in summary.items()]

        total_quantity = sum(summary.values())
        total_sales = sum([order.total for order in orders])

        return Response({
            "pie_chart": pie_chart,
            "total_quantity": total_quantity,
            "total_sales": total_sales
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from .models import Order, OrderItem

# ---------------- DAILY PROFITS ----------------
@api_view(["GET"])
def day_profits(request):
    data = (
        Order.objects.annotate(day=TruncDay("added_on"))
        .values("day")
        .annotate(total_sum=Sum("total"))
        .order_by("day")
    )

    result = [{"day": d["day"].strftime("%Y-%m-%d"), "total_sum": d["total_sum"]} for d in data]
    return Response(result)


# ---------------- WEEKLY PROFITS ----------------
@api_view(["GET"])
def week_profits(request):
    data = (
        Order.objects.annotate(week=TruncWeek("added_on"))
        .values("week")
        .annotate(total_sum=Sum("total"))
        .order_by("week")
    )

    result = [
        {"week": d["week"].strftime("%Y-%m-%d"), "total_sum": d["total_sum"]}
        for d in data
    ]
    return Response(result)


# ---------------- MONTHLY PROFITS ----------------
@api_view(["GET"])
def month_profits(request):
    data = (
        Order.objects.annotate(month=TruncMonth("added_on"))
        .values("month")
        .annotate(total_sum=Sum("total"))
        .order_by("month")
    )

    result = [
        {"month": d["month"].strftime("%Y-%m-%d"), "total_sum": d["total_sum"]}
        for d in data
    ]
    return Response(result)


# ---------------- ITEM PIE CHART FOR SPECIFIC DATE ----------------
@api_view(["GET"])
def orders_by_day(request, date):
    items = OrderItem.objects.filter(ordered_date__date=date)

    if not items.exists():
        return Response({"pie_chart": [], "total_quantity": 0, "total_sales": 0})

    pie_chart = (
        items.values("category__name")
        .annotate(quantity=Sum("quantity"))
        .order_by("category__name")
    )

    formatted = [
        {"name": p["category__name"], "quantity": p["quantity"]}
        for p in pie_chart
    ]

    total_quantity = sum(p["quantity"] for p in formatted)
    total_sales = sum(
        p["quantity"] * OrderItem.objects.filter(
            category__name=p["name"]
        ).first().category.price
        for p in formatted
    )

    return Response({
        "pie_chart": formatted,
        "total_quantity": total_quantity,
        "total_sales": total_sales,
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
from .models import OrderItem
from django.http import JsonResponse
@api_view(['GET'])
def orders_by_day(request, date):
    try:
        # Convert YYYY-MM-DD to datetime.date
        day = datetime.strptime(date, "%Y-%m-%d").date()

        # Filter by day
        items = OrderItem.objects.filter(ordered_date__date=day)

        if not items.exists():
            return Response({
                "pie_chart": [],
                "total_quantity": 0,
                "total_sales": 0
            })

        # Build pie chart data
        pie_chart = items.values("category__name").annotate(
            quantity=Sum("quantity")
        )

        total_quantity = items.aggregate(Sum("quantity"))["quantity__sum"]
        total_sales = sum([i.total_price for i in items])

        return Response({
            "pie_chart": [
                {"name": p["category__name"], "quantity": p["quantity"]}
                for p in pie_chart
            ],
            "total_quantity": total_quantity,
            "total_sales": total_sales
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
from django.db.models.functions import ExtractWeek
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
@api_view(['GET'])
def orders_by_week(request, week):
    try:
        # week format "YYYY-Www"
        year, week_num = week.split("-W")
        year = int(year)
        week_num = int(week_num)

        # Get Monday of that week
        first_day = datetime.strptime(f"{year}-W{week_num}-1", "%G-W%V-%u").date()
        last_day = first_day.replace(day=first_day.day + 6)

        items = OrderItem.objects.filter(
            ordered_date__date__range=[first_day, last_day]
        )

        if not items.exists():
            return Response({
                "pie_chart": [],
                "total_quantity": 0,
                "total_sales": 0
            })

        pie_chart = items.values("category__name").annotate(
            quantity=Sum("quantity")
        )

        total_quantity = items.aggregate(Sum("quantity"))["quantity__sum"]
        total_sales = sum(i.total_price for i in items)

        return Response({
            "pie_chart": [
                {"name": p["category__name"], "quantity": p["quantity"]}
                for p in pie_chart
            ],
            "total_quantity": total_quantity,
            "total_sales": total_sales
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(['GET'])
def orders_by_month(request, month):
    try:
        # month format "YYYY-MM"
        year, month_num = month.split("-")
        year = int(year)
        month_num = int(month_num)

        first_day = datetime(year, month_num, 1).date()

        # Get last day of month
        if month_num == 12:
            last_day = datetime(year, 12, 31).date()
        else:
            next_month = datetime(year, month_num + 1, 1).date()
            last_day = next_month.replace(day=next_month.day - 1)

        items = OrderItem.objects.filter(
            ordered_date__date__range=[first_day, last_day]
        )

        if not items.exists():
            return Response({
                "pie_chart": [],
                "total_quantity": 0,
                "total_sales": 0
            })

        pie_chart = items.values("category__name").annotate(
            quantity=Sum("quantity")
        )

        total_quantity = items.aggregate(Sum("quantity"))["quantity__sum"]
        total_sales = sum(i.total_price for i in items)

        return Response({
            "pie_chart": [
                {"name": p["category__name"], "quantity": p["quantity"]}
                for p in pie_chart
            ],
            "total_quantity": total_quantity,
            "total_sales": total_sales
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
