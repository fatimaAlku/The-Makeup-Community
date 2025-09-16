from django.db import models

# Create your models here.
from django.conf import settings


class Product(models.Model):
    FOUNDATION="foundation"
    LIPSTICK="lipstick"
    MASCARA="mascara"
    EYESHADOW="eyeshadow"
    CONCEALER="concealer"
    BLUSH="blush"
    HIGHLIGHTER="highlighter"
    SKINCARE="skincare"
    POWDER="powder"
    
    CATEGORY_CHOICES=[
        (FOUNDATION,"Foundation"),
        (LIPSTICK,"Lipstick"),
        (MASCARA,"Mascara"),
        (EYESHADOW,"Eyeshadow"),
        (CONCEALER,"Concealer"),
        (BLUSH,"Blush"),
        (HIGHLIGHTER,"Highlighter"),
        (SKINCARE,"Skincare"),
        (POWDER,"Powder"),
    ]
    
    brand=models.CharField(max_length=100)
    name=models.CharField(max_length=150)
    category=models.CharField(max_length=30,choices=CATEGORY_CHOICES)
    price=models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True)
    image_url = models.URLField(blank=True)   # product card image
    description = models.TextField(blank=True, help_text="Product description")
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"{self.brand} {self.name}"
    
    @property
    def average_rating(self):
        """Calculate average rating from all reviews"""
        from django.db.models import Avg
        return self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    @property
    def rating_distribution(self):
        """Get rating distribution for charts"""
        from django.db.models import Count
        return self.reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=120)
    body = models.TextField()
    rating = models.PositiveSmallIntegerField()  # 1–5 (validated in form)
    is_verified_purchase = models.BooleanField(default=False)
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True)
    
    # Additional review features
    helpful_votes = models.PositiveIntegerField(default=0)
    skin_type = models.CharField(max_length=50, blank=True, help_text="Oily, Dry, Combination, Sensitive, Normal")
    skin_tone = models.CharField(max_length=50, blank=True, help_text="Fair, Light, Medium, Tan, Deep")
    age_range = models.CharField(max_length=20, blank=True, help_text="18-24, 25-34, 35-44, 45-54, 55+")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta: 
        ordering = ["-created_at"]
        unique_together = ['user', 'product']  # One review per user per product
    
    def __str__(self): return f"{self.product} • {self.rating}/5 by {self.user}"
    
    @property
    def helpful_percentage(self):
        """Calculate helpful percentage if there are votes"""
        total_votes = self.helpful_votes + getattr(self, 'not_helpful_votes', 0)
        if total_votes == 0:
            return 0
        return (self.helpful_votes / total_votes) * 100

class ReviewMedia(models.Model):
    PHOTO = "photo"
    VIDEO = "video"
    KIND_CHOICES = [(PHOTO, "Photo"), (VIDEO, "Video")]
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="review_media/")
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)

    def __str__(self):
        return f"{self.kind} for {self.review_id}"

class ReviewHelpfulness(models.Model):
    """Track helpful votes on reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="helpfulness_votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()  # True for helpful, False for not helpful
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']  # One vote per user per review
    
    def __str__(self):
        return f"{'Helpful' if self.is_helpful else 'Not helpful'} vote by {self.user.username}"

class WearTest(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name="wear_test")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Wear test observations")

    def __str__(self):
        return f"WearTest for review {self.review_id}"