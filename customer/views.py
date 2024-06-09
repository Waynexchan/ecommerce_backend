from asyncio import Timeout
from django.shortcuts import render, redirect
from django.conf import settings
from store.models import Category, Tax, Product, Gallery, Specification, Size,Color, Cart, CartOrder , CartOrderItem, ProductFaq, Review, Wishlist, Notification, Coupon
from store.serializers import CouponSerializer, ProductSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer, NotificationSerializer
from userauths.models import User
import requests

from rest_framework import generics , status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from decimal import Decimal
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import stripe

class OrderAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny] #allowany only for testing now

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        orders = CartOrder.objects.filter(buyer=user, payment_status="paid")
        return orders
    
class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        order_oid = self.kwargs['order_oid']

        user = User.objects.get(id=user_id)

        order = CartOrder.objects.get(buyer=user, oid=order_oid , payment_status="paid")
        return order




