from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem, WishlistItem, Review
from decimal import Decimal
from django.contrib import messages
from django.views.decorators.http import require_POST
import uuid
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef, Avg, Count
from django.views.decorators.cache import never_cache
from .forms import ReviewForm

def home(request):
    products = Product.objects.filter(is_active=True)

    # Search products
    search_query = request.GET.get("q", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__icontains=search_query)
        )

    # Filter by category
    category = request.GET.get("category", "").strip()

    category_keywords = {
        "Electronics": "Electronics",
        "Fashion": "Fashion",
        "Home & Living": "Home",
        "Beauty & Personal Care": "Beauty",
        "Toys & Games": "Toys",
        "Books": "Books",
        "Kitchen & Dining": "Kitchen",
        "Sports & Fitness": "Sports",
    }

    if category:
        keyword = category_keywords.get(category)

        if keyword:
            products = products.filter(category__icontains=keyword)
        else:
            products = products.none()

    # Sort products
    sort = request.GET.get("sort", "")

    if sort == "price_low":
        products = products.order_by("price", "pk")
    elif sort == "price_high":
        products = products.order_by("-price", "pk")
    elif sort == "name":
        products = products.order_by("name", "pk")
    else:
        products = products.order_by("-created_at", "-pk")

    # Show which products are already wishlisted by this user
    if request.user.is_authenticated:
        products = products.annotate(
            is_wishlisted=Exists(
                WishlistItem.objects.filter(
                    user=request.user,
                    product_id=OuterRef("pk")
                )
            )
        )

    products = products.annotate(
        average_rating=Avg("reviews__rating"),
        total_reviews=Count("reviews")
    )
        
    # Paginate: 12 products per page
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "store/home.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
        },
    )

def product_detail(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related("user")

    review_stats = reviews.aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id")
    )

    existing_review = None

    if request.user.is_authenticated:
        existing_review = reviews.filter(
            user=request.user
        ).first()

    return render(
        request,
        "store/product_detail.html",
        {
         "product": product,
         "reviews": reviews,
         "average_rating": review_stats["average_rating"],
         "total_reviews": review_stats["total_reviews"],
         "existing_review": existing_review,
        },
    )


def get_cart(request):
    return request.session.get("cart", {})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("store:product_detail", pk=pk)

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("store:product_detail", pk=pk)

    cart = get_cart(request)
    new_quantity = int(cart.get(str(pk), 0)) + quantity

    # if new_quantity > product.stock:
    #     messages.error(request, "Not enough stock available.")
    #     return redirect("store:product_detail", pk=pk)
    if new_quantity > product.stock:
        if product.stock == 1:
            messages.error(request, "Only 1 stock left.")
        else:
            messages.error(
                request,
                f"Only {product.stock} stocks left."
            )

        return redirect("store:product_detail", pk=pk)

    cart[str(pk)] = new_quantity
    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, "Product added to your cart!")
    return redirect("store:cart")


def cart_detail(request):
    cart = get_cart(request)
    items = []
    total = Decimal("0.00")

    products = Product.objects.filter(
        pk__in=cart.keys(),
        is_active=True,
    )

    for product in products:
        quantity = int(cart[str(product.pk)])
        subtotal = product.price * quantity

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

        total += subtotal

    return render(
        request,
        "store/cart.html",
        {"items": items, "total": total},
    )


@require_POST
def cart_remove(request, pk):
    cart = get_cart(request)
    cart.pop(str(pk), None)

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, "Item removed from your cart.")
    return redirect("store:cart")

@never_cache
@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")

    products = Product.objects.filter(
        pk__in=cart.keys(),
        is_active=True,
    )

    for product in products:
        quantity = int(cart[str(product.pk)])
        subtotal = product.price * quantity

        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })
        total += subtotal

    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("store:cart")

    if request.method == "POST":
        address = request.POST.get("delivery_address", "").strip()

        if not address:
            messages.error(request, "Please enter a delivery address.")
            return render(request, "store/checkout.html", {
                "items": items,
                "total": total,
            })

        try:
            with transaction.atomic():
                # Lock the products while checking and updating stock.
                locked_products = {
                    p.pk: p
                    for p in Product.objects.select_for_update().filter(
                        pk__in=[item["product"].pk for item in items]
                    ).order_by("pk")
                }

                verified_items = []
                verified_total = Decimal("0.00")

                for item in items:
                    product = locked_products.get(item["product"].pk)
                    quantity = item["quantity"]

                    if (
                        product is None
                        or not product.is_active
                        or quantity < 1
                        or product.stock < quantity
                    ):
                        raise ValueError(
                            "A product is unavailable or has insufficient stock. "
                            "Please review your cart."
                        )

                    subtotal = product.price * quantity
                    verified_total += subtotal

                    verified_items.append({
                        "product": product,
                        "quantity": quantity,
                        "unit_price": product.price,
                    })

                order = Order.objects.create(
                    user=request.user,
                    order_number=uuid.uuid4().hex[:20].upper(),
                    delivery_address=address,
                    total_amount=verified_total,
                )

                for item in verified_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                    )

                    item["product"].stock -= item["quantity"]
                    item["product"].save(update_fields=["stock"])

        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("store:cart")

        request.session["cart"] = {}
        request.session.modified = True

        return redirect(
            "store:order_confirmation",
            order_id=order.pk,
        )

    return render(request, "store/checkout.html", {
        "items": items,
        "total": total,
    })


@never_cache
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id,
        user=request.user,
    )

    return render(
        request,
        "store/order_confirmation.html",
        {"order": order},
    )


@never_cache
@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "store/order_history.html",
        {"orders": orders},
    )

@never_cache
@login_required
@require_POST
def cancel_order(request, order_id):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            pk=order_id,
            user=request.user,
        )

        # Only pending or confirmed orders can be cancelled.
        if order.status not in ("PENDING", "CONFIRMED"):
            messages.error(
                request,
                "This order can no longer be cancelled.",
            )
            return redirect("store:order_history")

        items = list(order.items.all())

        # Lock products before restoring their stock.
        product_ids = sorted({
            item.product_id for item in items
        })

        locked_products = {
            product.pk: product
            for product in Product.objects.select_for_update()
            .filter(pk__in=product_ids)
            .order_by("pk")
        }

        for item in items:
            product = locked_products.get(item.product_id)

            if product is not None:
                product.stock += item.quantity
                product.save(update_fields=["stock"])

        order.status = "CANCELLED"
        order.save(update_fields=["status"])

    messages.success(
        request,
        f"Order {order.order_number} has been cancelled.",
    )
    return redirect("store:order_history")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Your account has been created successfully!"
            )
            return redirect("store:home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def wishlist_detail(request):
    wishlist_items = WishlistItem.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "store/wishlist.html",
        {"wishlist_items": wishlist_items}
    )


@login_required
@require_POST
def wishlist_add(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True
    )

    _, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(
            request,
            f"{product.name} added to your wishlist."
        )
    else:
        messages.info(
            request,
            f"{product.name} is already in your wishlist."
        )

    return redirect("store:product_detail", pk=product.pk)


@login_required
@require_POST
def wishlist_remove(request, pk):
    wishlist_item = get_object_or_404(
        WishlistItem,
        pk=pk,
        user=request.user
    )

    product_name = wishlist_item.product.name
    wishlist_item.delete()

    messages.success(
        request,
        f"{product_name} removed from your wishlist."
    )

    return redirect("store:wishlist")


@login_required
@require_POST
def wishlist_toggle(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        is_active=True
    )

    wishlist_item = WishlistItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed from wishlist.")
    else:
        WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        messages.success(request, f"{product.name} added to wishlist.")

    return redirect(request.POST.get("next") or "store:home")


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    existing_review = Review.objects.filter(
        user=request.user,
        product=product
    ).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing_review)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()

            messages.success(request, "Your review has been saved.")
            return redirect("store:product_detail", pk=product.pk)
    else:
        form = ReviewForm(instance=existing_review)

    return render(
        request,
        "store/add_review.html",
        {
            "product": product,
            "form": form,
            "existing_review": existing_review,
        },
    )


@login_required
def track_order(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id,
        user=request.user
    )

    tracking_steps = [
        {
            "status": "PENDING",
            "label": "Order Placed",
            "description": "Your order has been received."
        },
        {
            "status": "CONFIRMED",
            "label": "Order Confirmed",
            "description": "Your order has been confirmed."
        },
        {
            "status": "SHIPPED",
            "label": "Shipped",
            "description": "Your order is on its way."
        },
        {
            "status": "DELIVERED",
            "label": "Delivered",
            "description": "Your order has been delivered."
        },
    ]

    status_order = [
        "PENDING",
        "CONFIRMED",
        "SHIPPED",
        "DELIVERED",
    ]

    if order.status == "CANCELLED":
        current_step = -1
    else:
        current_step = status_order.index(order.status)

    return render(
        request,
        "store/track_order.html",
        {
            "order": order,
            "tracking_steps": tracking_steps,
            "current_step": current_step,
        },
    )
