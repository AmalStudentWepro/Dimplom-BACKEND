from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartItemCreateSerializer, CartSerializer


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        return cart


class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )   