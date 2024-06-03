from django.shortcuts import render

from store.models import Category, Tax, Product, Gallery, Specification, Size,Color, Cart, CartOrder , CartOrderItem, ProductFaq, Review, Wishlist, Notification, Coupon
from store.serializers import ProductSerializer, CategorySerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer
from userauths.models import User

from rest_framework import generics , status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from decimal import Decimal

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all() #to list all of the product
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class ProductDetailAPIView(generics.RetrieveAPIView): #get one single item
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_object(self): # use slug to search specific product
        slug = self.kwargs['slug']
        return Product.objects.get(slug=slug)
    
class CartAPIView(generics.ListCreateAPIView): 
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        payload = request.data

        product_id = payload['product_id']
        user_id = payload['user_id']
        qty = payload['qty']
        price = payload['price']
        shipping_amount = payload['shipping_amount']
        country = payload['country']
        size = payload['size']
        color = payload['color']
        cart_id = payload['cart_id']
        
        product = Product.objects.get(id=product_id)

        if user_id != "undefined":
            user = User.objects.get(id=user_id)
        else:
            user = None # for guess 

        tax = Tax.objects.filter(country=country).first()
        if tax:
            tax_rate = tax.rate / 100
        else:
            tax_rate = 0

        cart = Cart.objects.filter(cart_id=cart_id, product=product).first()

        # fix percentage
        service_fee_percentage = Decimal('0.10')  # 10%

        if cart:
            cart.product = product
            cart.user = user
            cart.qty = qty
            cart.price = price
            cart.sub_total = Decimal(price) * int(qty)
            cart.shipping_amount = Decimal(shipping_amount) * int(qty)
            cart.tax_fee = cart.sub_total * Decimal(tax_rate)
            cart.color = color
            cart.size = size
            cart.country = country
            cart.cart_id = cart_id

            cart.service_fee = service_fee_percentage * cart.sub_total

            cart.total = cart.sub_total + cart.shipping_amount + cart.service_fee + cart.tax_fee
            cart.save()

            return Response({'message': "Cart Update Successfully"}, status=status.HTTP_200_OK)
        
        else:
            cart = Cart(
                product=product,
                user=user,
                qty=qty,
                price=price,
                sub_total=Decimal(price) * int(qty),
                shipping_amount=Decimal(shipping_amount) * int(qty),
                tax_fee=Decimal(price) * int(qty) * Decimal(tax_rate),
                color=color,
                size=size,
                country=country,
                cart_id=cart_id,
            )

            cart.service_fee = service_fee_percentage * cart.sub_total

            cart.total = cart.sub_total + cart.shipping_amount + cart.service_fee + cart.tax_fee
            cart.save()

            return Response({'message': "Cart Create Successfully"}, status=status.HTTP_201_CREATED)
