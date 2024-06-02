from django.shortcuts import render

from store.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

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