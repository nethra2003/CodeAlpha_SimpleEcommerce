from django.db import models
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, default="General")
    image = models.ImageField(
        upload_to="products/",
        blank=True,
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=30, unique=True)
    delivery_address = models.TextField()
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_wishlist_product"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review"
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_between_1_and_5"
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5 by {self.user}"
