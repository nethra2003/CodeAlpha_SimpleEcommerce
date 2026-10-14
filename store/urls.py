from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/",views.cart_remove,name="cart_remove"),
    path("accounts/signup/", views.signup, name="signup"),
    path("checkout/", views.checkout, name="checkout"),
    path(
    "orders/<int:order_id>/confirmation/",
    views.order_confirmation,
    name="order_confirmation",
    ),
    path("orders/", views.order_history, name="order_history"),
    path(
    "orders/<int:order_id>/cancel/",
    views.cancel_order,
    name="cancel_order",
    ),
    path("wishlist/", views.wishlist_detail, name="wishlist"),
    path("wishlist/add/<int:pk>/", views.wishlist_add, name="wishlist_add"),
    path("wishlist/remove/<int:pk>/", views.wishlist_remove, name="wishlist_remove"),
    path("wishlist/toggle/<int:pk>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("products/<int:pk>/review/", views.add_review, name="add_review"),
    path("orders/<int:order_id>/track/", views.track_order, name="track_order",
),
]


