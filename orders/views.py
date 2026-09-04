from django.db import transaction
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )
        cart_items = cart.items.select_related("product")

        if not cart_items.exists():
            raise ValidationError("Корзина пуста.")

        for item in cart_items:
            if item.quantity > item.product.stock:
                raise ValidationError(
                    f"Недостаточно товара: {item.product.name}"
                )

        order = Order.objects.create(
            user=request.user,
            status=Order.Status.NEW,
        )

        order_items = []

        for item in cart_items:
            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_order=item.product.price,
                )
            )

            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])

        OrderItem.objects.bulk_create(order_items)

        cart_items.delete()

        serializer = self.get_serializer(order)

        return Response(
            serializer.data,
            status=201,
        )
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
        )