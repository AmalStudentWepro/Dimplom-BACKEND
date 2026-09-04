from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import ProductFilter
from .models import Category, Product
from .permissions import IsAdminUser
from .serializers import CategorySerializer, ProductSerializer


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_class = ProductFilter
    search_fields = ("name", "description")
    ordering_fields = (
        "price",
        "created_at",
        "popularity",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        return (
            Product.objects.all()
            .annotate(
                popularity=Coalesce(
                    Sum("order_items__quantity"),
                    Value(0),
                )
            )
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer