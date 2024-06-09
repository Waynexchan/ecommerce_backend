from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from userauths import views as userauths_views
from store import views as store_views
from customer import views as customer_views


urlpatterns = [
    path('user/token/', userauths_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', userauths_views.RegisterView.as_view(), name='auth_register'),
    path('user/password-reset/<email>', userauths_views.PasswordResetEmailVerify.as_view(), name='user_profile'),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view(), name='password_change'),
    path('user/profile/<user_id>/', userauths_views.ProfileView.as_view(), name='profile-view'),

    # Store Endpoints
    path('category/', store_views.CategoryListAPIView.as_view()),
    path('products/', store_views.ProductListAPIView.as_view()),
    path('products/<slug>/', store_views.ProductDetailAPIView.as_view()),
    path('cart-view/', store_views.CartAPIView.as_view()), #to add items into the cart
    #Separate to two different urls
    path('cart-list/<str:cart_id>/<int:user_id>/', store_views.CartListView.as_view()),
    path('cart-list/<str:cart_id>/', store_views.CartListView.as_view()),
    #cart detail
    path('cart-detail/<str:cart_id>/', store_views.CartDetailView.as_view()),
    path('cart-detail/<str:cart_id>/<int:user_id>/', store_views.CartDetailView.as_view()),
    #Delete cart
    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/', store_views.CartItemDeleteAPIView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/', store_views.CartItemDeleteAPIView.as_view()),
    path('create-order/', store_views.CreateOrderAPIView.as_view()),
    path('checkout/<str:order_oid>/', store_views.CheckoutView.as_view()),
    path('coupon/', store_views.CouponAPIView.as_view()),
    path('reviews/<int:product_id>/', store_views.ReviewListAPIView.as_view()),
    path('search/', store_views.SearchProductAPIView.as_view()),



    # Payment Endpoints
    path('stripe-checkout/<str:order_oid>/', store_views.StripeCheckoutView.as_view(), name='stripe-checkout'),
    path('payment-success/<str:order_oid>/', store_views.PaymentSuccessView.as_view(), name='paypal-checkout'),

    # Customer EndPoints
    path('customer/orders/<int:user_id>/', customer_views.OrderAPIView.as_view(), name='customer-orders'),
    path('customer/order/<int:user_id>/<str:order_oid>/', customer_views.OrderDetailAPIView.as_view(), name='customer-order-detail'),


]