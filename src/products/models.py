from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Category(models.Model):
    """A product category such as 'boys', 'girls', or 'toys'."""

    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=50, unique=True, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the category's name."""
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"


class Tag(models.Model):
    """A label that can be attached to products via a many-to-many relation."""

    name = models.CharField(max_length=50, unique=True, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return the tag's name."""
        return self.name


class Product(models.Model):
    """A product in the shop, optionally tagged and rated by users."""

    category = models.ForeignKey(Category, null=True, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to="imgs/products/", null=True, blank=True)
    name = models.CharField(max_length=80, blank=False, null=False)
    tags = models.ManyToManyField(Tag, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW helper properties
    @property
    def average_rating(self):
        """Return the average rating across all comments, or 0 if there are none."""
        from django.db.models import Avg

        return self.comments.aggregate(a=Avg("rating"))["a"] or 0

    @property
    def rating_count(self):
        """Return the number of comments (ratings) for this product."""
        return self.comments.count()

    def __str__(self) -> str:
        """Return the product's name."""
        return self.name


# NEW model
class Comment(models.Model):
    """A user or guest review for a product, with a rating and optional text."""

    product = models.ForeignKey(Product, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    guest_name = models.CharField(max_length=80, blank=True)
    guest_email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name="comment_rating_range"),
            models.UniqueConstraint(
                fields=["product", "user"], name="unique_user_product_comment", condition=models.Q(user__isnull=False)
            ),
        ]
        indexes = [models.Index(fields=["product", "created_at"])]

    def __str__(self):
        """Return a short label with the author and rating."""
        who = self.user.username if self.user else (self.guest_name or "Guest")
        return f"{who} - {self.rating}★"
