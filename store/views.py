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



stripe.api_key = settings.STRIPE_SECRET_KEY

def send_notification(user=None, vendor=None, order=None, order_item=None):
    Notification.objects.create(
        user = user,
        vendor = vendor,
        order = order,
        order_item = order_item
    )

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

            cart.service_fee = Decimal(service_fee_percentage) * cart.sub_total

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
        
class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    queryset = Cart.objects.all()

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = User.objects.filter(id=user_id).first()  # Ensure only one user is returned
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)

        return queryset  # Return all matching items
    
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]
    lookup_field = "cart_id"

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = User.objects.filter(id=user_id).first()  # Ensure only one user is returned
            queryset = Cart.objects.filter(user=user, cart_id=cart_id)
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)

        return queryset  # Return all matching items

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_shipping = 0.0
        total_tax = 0.0
        total_service_fee = 0.0
        total_sub_total = 0.0
        total_total = 0.0

        for cart_item in queryset:
            total_shipping += float(self.calculate_shipping(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_service_fee += float(self.calculate_service_fee(cart_item))
            total_sub_total += float(self.calculate_sub_total(cart_item))
            total_total += float(self.calculate_total(cart_item))

        data = {
            'shipping': total_shipping,
            'tax': total_tax,
            'service_fee': total_service_fee,
            'sub_total': total_sub_total,
            'total': total_total,
        }

        return Response(data)

    def calculate_shipping(self, cart_item):
        return cart_item.shipping_amount
        
    def calculate_tax(self, cart_item):
        return cart_item.tax_fee
        
    def calculate_service_fee(self, cart_item):
        return cart_item.service_fee
        
    def calculate_sub_total(self, cart_item):
        return cart_item.sub_total
        
    def calculate_total(self, cart_item):
        return cart_item.total
    

class CartItemDeleteAPIView(generics.DestroyAPIView): # delete item
    serializer_class = CartSerializer
    lookup_field = 'cart_id'

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        user_id = self.kwargs.get('user_id') #won't break the program if user id does not exist

        if user_id:
            user = User.objects.get(id=user_id)
            cart = Cart.objects.get(id=item_id, cart_id=cart_id, user=user)
        else:
            cart = Cart.objects.get(id=item_id, cart_id=cart_id)

        return cart
        
class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = [AllowAny]

    def create(self, request):
        payload = request.data  # get data from frontend

        full_name = payload['full_name']
        email = payload['email']
        mobile = payload['mobile']
        address = payload['address']
        city = payload['city']
        state = payload['state']
        country = payload['country']
        cart_id = payload['cart_id']
        user_id = payload['user_id']

        user = User.objects.get(id=user_id) if user_id != 0 else None

        cart_items = Cart.objects.filter(cart_id=cart_id)

        total_shipping = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_service_fee = Decimal(0.00)
        total_sub_total = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)

        order = CartOrder.objects.create(
            full_name=full_name,
            email=email,
            mobile=mobile,
            address=address,
            city=city,
            state=state,
            country=country,
            buyer=user,  # Assign buyer here
        )

        for c in cart_items:
            CartOrderItem.objects.create(
                order=order,
                product=c.product,
                vendor=c.product.vendor,
                qty=c.qty,
                color=c.color,
                size=c.size,
                price=c.price,
                sub_total=c.sub_total,
                shipping_amount=c.shipping_amount,
                service_fee=c.service_fee,
                tax_fee=c.tax_fee,
                total=c.total,
                initial_total=c.total,
            )

            total_shipping += Decimal(c.shipping_amount)
            total_tax += Decimal(c.tax_fee)
            total_service_fee += Decimal(c.service_fee)
            total_sub_total += Decimal(c.sub_total)
            total_initial_total += Decimal(c.total)
            total_total += Decimal(c.total)

            order.vendor.add(c.product.vendor)

        order.sub_total = total_sub_total
        order.shipping_amount = total_shipping
        order.tax_fee = total_tax
        order.service_fee = total_service_fee
        order.initial_total = total_initial_total
        order.total = total_total

        order.save()

        return Response({"message": "Order Created Successfully", "order_oid": order.oid}, status=status.HTTP_201_CREATED)

    
class CheckoutView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    lookup_field = 'order_oid'

    def get_object(self):
        order_oid = self.kwargs['order_oid']
        order = CartOrder.objects.get(oid=order_oid)
        return order

class CouponAPIView(generics.CreateAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()
    permission_classes = [AllowAny]

    def create(self, request):
        payload = request.data

        order_oid = payload['order_oid']
        coupon_code = payload['coupon_code']

        try:
            order = CartOrder.objects.get(oid=order_oid)
            coupon = Coupon.objects.filter(code=coupon_code).first()

            if coupon:
                order_items = CartOrderItem.objects.filter(order=order, vendor=coupon.vendor)
                if order_items.exists():
                    for i in order_items:
                        if not coupon in i.coupon.all(): # Check if the coupon is already applied
                            discount = i.total * coupon.discount / 100

                            i.total -= discount
                            i.sub_total -= discount
                            i.coupon.add(coupon)
                            i.saved += discount

                            order.total -= discount
                            order.sub_total -= discount
                            order.saved += discount

                            i.save()
                            order.save()

                            return Response({"message": "Coupon Activated", "icon":"success"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"message": "Coupon Already Activated", "icon":"warning"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Order Item Does Not Exist", "icon":"error"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Coupon Does Not Exist", "icon":"error"}, status=status.HTTP_200_OK)
        except CartOrder.DoesNotExist:
            return Response({"message": "Order Does Not Exist", "icon":"error"}, status=status.HTTP_404_NOT_FOUND)
        except Coupon.DoesNotExist:
            return Response({"message": "Coupon Does Not Exist", "icon":"error"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StripeCheckoutView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = CartOrder.objects.all()

    def post(self, request, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        try:
            order = CartOrder.objects.get(oid=order_oid)
        except CartOrder.DoesNotExist:
            return Response({"message": "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'USD',
                            'product_data': {
                                'name': f"Order {order.oid}"
                            },
                            'unit_amount': int(order.total * 100),  # Convert to cents
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=f'http://localhost:5173/payment-success/{order.oid}/?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'http://localhost:5173/payment-failed/?session_id={{CHECKOUT_SESSION_ID}}'
            )

            order.stripe_session_id = checkout_session.id
            order.save()

            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response({"error": f"Something went wrong while creating the checkout session: {str(e)}"})


def get_access_token(client_id, secret_id):
    token_url = 'https://api.sandbox.paypal.com/v1/oauth2/token' # use live api key later
    data = {'grant_type' : 'client_credentials'}
    auth = (client_id, secret_id)
    response = requests.post(token_url, data=data , auth=auth)
    if response.status_code == 200:
        print("Access Token:" , response.json()['access_token'])
        return response.json()['access_token']
    else:
        raise Exception(f"Falied to get access token: {response.status_code}")

import requests
from requests.exceptions import Timeout, HTTPError

class PaymentSuccessView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = CartOrder.objects.all()

    def post(self, request, *args, **kwargs):
        payload = request.data

        order_oid = payload.get('order_oid')
        session_id = payload.get('session_id')
        paypal_order_id = payload.get('paypal_order_id')

        print("paypal_order_id =====", paypal_order_id)

        try:
            order = CartOrder.objects.get(oid=order_oid)
        except CartOrder.DoesNotExist:
            return Response({"message": "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        order_items = CartOrderItem.objects.filter(order=order)

        # Paypal Payment
        if paypal_order_id and paypal_order_id != 'null':
            paypal_api_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {get_access_token(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_ID)}'
            }

            try:
                response = requests.get(paypal_api_url, headers=headers, timeout=10)
                response.raise_for_status()
                if response.status_code == 200:
                    paypal_order_data = response.json()  # response from paypal
                    paypal_payment_status = paypal_order_data['status']
                    if paypal_payment_status == "COMPLETED":
                        if order.payment_status == "pending":
                            order.payment_status = 'paid'
                            order.save()

                            # send Notifications to customers
                            if order.buyer is not None:
                                send_notification(user=order.buyer, order=order)

                            # send Notifications to vendors
                            for o in order_items:
                                send_notification(vendor=o.vendor, order=order, order_item=o)

                                # send Email to Vendor
                                try:
                                    context = {
                                        'order': order,
                                        'order_items': order_items,
                                        'vendor': o.vendor,
                                    }
                                    subject = "New Sale"
                                    text_body = render_to_string("email/vendor_sale.txt", context)
                                    html_body = render_to_string("email/vendor_sale.html", context)
                                    
                                    msg = EmailMultiAlternatives(
                                        subject=subject,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        to=[o.vendor.user.email],
                                        body=text_body
                                    )
                                    msg.attach_alternative(html_body, "text/html")
                                    msg.send()
                                except Exception as e:
                                    print(f"Failed to send email to vendor: {e}")
                                    pass

                            # send Email To Buyer
                            try:
                                context = {
                                    'order': order,
                                    'order_items': order_items,
                                }
                                subject = "Order Placed Successfully"
                                text_body = render_to_string("email/customer_order_confirmation.txt", context)
                                html_body = render_to_string("email/customer_order_confirmation.html", context)
                                
                                msg = EmailMultiAlternatives(
                                    subject=subject,
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    to=[order.email],
                                    body=text_body
                                )
                                msg.attach_alternative(html_body, "text/html")
                                msg.send()
                            except Exception as e:
                                print(f"Failed to send email to buyer: {e}")
                                pass
                        
                            return Response({"message": "Payment Successful"})
                        else:
                            return Response({"message": "Already Paid"})
                    else:
                        return Response({"message": "Your Invoice is unpaid"})

            except Timeout:
                return Response({"message": "Request to PayPal timed out. Please try again later."}, status=status.HTTP_408_REQUEST_TIMEOUT)
            except requests.exceptions.RequestException as e:
                return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Stripe Payment
        if session_id and session_id != 'null':
            try:
                session = stripe.checkout.Session.retrieve(session_id)  # retrieve particular session id

                if session.payment_status == "paid":
                    if order.payment_status == "pending":
                        order.payment_status = 'paid'
                        order.save()

                        # send Notifications to customers
                        if order.buyer is not None:
                            send_notification(user=order.buyer, order=order)

                        # send Notifications to vendors
                        for o in order_items:
                            send_notification(vendor=o.vendor, order=order, order_item=o)

                            # send Email to Vendor
                            try:
                                context = {
                                    'order': order,
                                    'order_items': order_items,
                                    'vendor': o.vendor,
                                }
                                subject = "New Sale"
                                text_body = render_to_string("email/vendor_sale.txt", context)
                                html_body = render_to_string("email/vendor_sale.html", context)
                                
                                msg = EmailMultiAlternatives(
                                    subject=subject,
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    to=[o.vendor.user.email],
                                    body=text_body
                                )
                                msg.attach_alternative(html_body, "text/html")
                                msg.send()
                            except Exception as e:
                                print(f"Failed to send email to vendor: {e}")
                                pass

                        # send Email To Buyer
                        try:
                            context = {
                                'order': order,
                                'order_items': order_items,
                            }
                            subject = "Order Placed Successfully"
                            text_body = render_to_string("email/customer_order_confirmation.txt", context)
                            html_body = render_to_string("email/customer_order_confirmation.html", context)
                            
                            msg = EmailMultiAlternatives(
                                subject=subject,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                to=[order.email],
                                body=text_body
                            )
                            msg.attach_alternative(html_body, "text/html")
                            msg.send()
                        except Exception as e:
                            print(f"Failed to send email to buyer: {e}")
                            pass
                    
                        return Response({"message": "Payment Successful"})
                    else:
                        return Response({"message": "Already Paid"})
                elif session.payment_status == "unpaid":
                    return Response({"message": "Your Invoice is Unpaid"})
                elif session.payment_status == "cancelled":
                    return Response({"message": "Your Invoice was cancelled"})
                else:
                    return Response({"message": "An Error occurred, Try Again ..."})
            except stripe.error.StripeError as e:
                return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "Invalid session ID"})


class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs['product_id']

        product = Product.objects.get(id=product_id)
        reviews = Review.objects.filter(product=product)
        return reviews
    
    def create(self, request, *args, **kwargs):
        payload = request.data

        user_id = payload['user_id']
        product_id = payload['product_id']
        rating = payload['rating']
        review = payload['review']

        user = User.objects.get(id = user_id)
        product = Product.objects.get(id = product_id)

        Review.objects.create(
            user = user,
            product = product,
            rating = rating,
            review = review
        )

        return Response({"message": "Review Created Successfully"}, status=status.HTTP_200_OK)
    
class SearchProductAPIView(generics.ListCreateAPIView):
    serializer_class =ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get("query") # get query from frontend
        products = Product.objects.filter(status="published", title__icontains=query) #check all of the title
        return products
