from django.urls import path
from . import views
from .views import CategoryListCreate,DaywiseProfits,ProductList


urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('viewcart/',views.Getcart.as_view(),name='cart'),
    path('Order/',views.Orderitem.as_view(),name='order'),
    path('dayprofits/',DaywiseProfits.as_view(),name='profits'),
    path('updatecart/<int:pk>/', views.update_cart, name='update_cart'),
    path('deletecart/<int:pk>/', views.delete_cart_item, name='delete_cart_item'),
    path('logout/', views.logout_user, name='logout_user'),
    path('address/',views.add_address,name='address'),
    path('get_addresses/', views.get_addresses, name='get_addresses'),
    path('product/',ProductList.as_view(),name='product'),
    path('allorders/',views.Orderitems1.as_view(),name='Allorders'),
    path("dayprofits/", views.day_profits,name="day_profits"),
    path("weekprofits/", views.week_profits,name="week_profits"),
    path("monthprofits/", views.month_profits,name="month_profits"),
    path("orders-by-day/<str:date>/", views.orders_by_day,name="orders_by_day"),
    path("orders-by-week/<str:week>/", views.orders_by_week,name="orders_by_week"),
    path("orders-by-month/<str:month>/", views.orders_by_month,name="orders_by_month"),
   
]

