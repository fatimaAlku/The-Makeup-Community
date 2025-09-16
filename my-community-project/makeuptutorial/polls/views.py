from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Product, Review, WearTest, ReviewHelpfulness
from django.views.generic import TemplateView, ListView
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q, F, Value, FloatField, Case, When
from django.db.models.functions import Coalesce
from django.contrib import messages
from .forms import ReviewForm, ReviewMediaFormSet, ReviewHelpfulnessForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.views.generic import FormView
from .forms import SignUpForm 

class ProductList(generic.ListView):
    model = Product
    template_name = "polls/home.html"      # use a dedicated home template
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.all().annotate(
            avg_rating=Avg("reviews__rating"),
            reviews_count=Count("reviews"),
        )
        return qs.order_by("-id")  # newest first

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Add KPI data for homepage
        ctx["kpi_products"] = Product.objects.count()
        ctx["kpi_reviews"] = Review.objects.count()
        ctx["kpi_users"] = get_user_model().objects.count()
        
        return ctx

class ProductDetail(generic.DetailView):
    model = Product
    template_name = "polls/product_detail.html"

class ProductCreate(LoginRequiredMixin, generic.CreateView):
    model = Product
    fields = ["brand","name","category","price"]
    template_name = "polls/form.html"
    def get_success_url(self): return reverse("product-detail", args=[self.object.pk])

class ProductUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Product
    fields = ["brand","name","category","price"]
    template_name = "polls/form.html"
    def get_success_url(self): return reverse("product-detail", args=[self.object.pk])

class ProductDelete(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = "polls/confirm_delete.html"
    success_url = reverse_lazy("product-list")

class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self): return self.get_object().user == self.request.user


class ReviewUpdate(LoginRequiredMixin, AuthorRequiredMixin, generic.UpdateView):
    model = Review
    fields = ["title","body","rating"]
    template_name = "polls/form.html"
    def get_success_url(self): return reverse("product-detail", args=[self.object.product_id])

class ReviewDelete(LoginRequiredMixin, AuthorRequiredMixin, generic.DeleteView):
    model = Review
    template_name = "polls/confirm_delete.html"
    def get_success_url(self): return reverse("product-detail", args=[self.object.product_id])





# About
class AboutView(TemplateView):
    template_name = "polls/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        User = get_user_model()
        ctx.update({
            "kpi_products": Product.objects.count(),
            "kpi_reviews": Review.objects.count(),
            "kpi_users": User.objects.count(),
        })
        return ctx
    

# Product page
class ProductBrowse(ListView):
    model = Product
    template_name = "polls/products.html"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects.all()
            .annotate(
                avg_rating=Avg("reviews__rating"),
                reviews_count=Count("reviews"),
            )
        )
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(category__icontains=q))

        cat = self.request.GET.get("category") or ""
        if cat:
            qs = qs.filter(category=cat)

        # price filters (min/max are optional)
        pmin = self.request.GET.get("min")
        pmax = self.request.GET.get("max")
        if pmin:
            qs = qs.filter(price__gte=pmin)
        if pmax:
            qs = qs.filter(price__lte=pmax)

        sort = self.request.GET.get("sort") or "rating"
        sort_map = {
            "newest": "-id",
            "rating": "-avg_rating",
            "reviewed": "-reviews_count",
            "price_asc": "price",
            "price_desc": "-price",
            "name": "name",
        }
        return qs.order_by(sort_map.get(sort, "-id"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # choices for the category select
        ctx["categories"] = dict(Product._meta.get_field("category").choices)
        # preserve current filters in pagination links (minus page)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["qs"] = params.urlencode()
        # echo current selections
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["price_min"] = self.request.GET.get("min", "")
        ctx["price_max"] = self.request.GET.get("max", "")
        ctx["sort"] = self.request.GET.get("sort", "rating")
        
        # Add statistics for the hero section
        ctx["total_reviews"] = Review.objects.count()
        ctx["active_reviewers"] = get_user_model().objects.filter(reviews__isnull=False).distinct().count()
        
        return ctx
    

# Trend page
class TrendsView(ListView):
    model = Product
    template_name = "polls/trends.html"
    paginate_by = 12

    def get_queryset(self):
        # window size (days) – defaults to 30, accepts 7/14/30/60 via ?days=
        try:
            days = int(self.request.GET.get("days", 30))
        except ValueError:
            days = 30
        days = max(1, min(days, 90))
        since = timezone.now() - timedelta(days=days)

        cat = self.request.GET.get("category") or ""

        qs = (
            Product.objects.all()
            .annotate(
                reviews_count=Count("reviews"),
                recent_reviews=Count("reviews", filter=Q(reviews__created_at__gte=since)),
                avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
                recent_avg=Coalesce(Avg("reviews__rating", filter=Q(reviews__created_at__gte=since)), Value(0.0)),
            )
        )

        # positive rating delta (recent vs lifetime), negatives clamp to 0
        qs = qs.annotate(
            rating_delta_pos=Case(
                When(recent_avg__gt=F("avg_rating"), then=F("recent_avg") - F("avg_rating")),
                default=Value(0.0),
                output_field=FloatField(),
            )
        )

        # trending score (tweak weights if you like)
        # 0.7 * recent review count  +  0.2 * recent average (scaled)  +  0.1 * positive rating delta (scaled)
        qs = qs.annotate(
            trending_score=(
                0.7 * F("recent_reviews")
                + 0.2 * F("recent_avg") * 5.0
                + 0.1 * F("rating_delta_pos") * 10.0
            )
        )

        if cat:
            qs = qs.filter(category=cat)

        return qs.order_by("-trending_score", "-recent_reviews", "-id")

    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # parse days as an int for clean comparisons
        try:
            selected_days = int(self.request.GET.get("days", 30))
        except ValueError:
            selected_days = 30

        ctx.update({
            "days": selected_days,                                  # int
            "day_options": [7, 14, 30, 60],                         # <-- pass list to template
            "categories": dict(Product._meta.get_field("category").choices),
            "selected_category": self.request.GET.get("category", ""),
        })

        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["qs"] = params.urlencode()
        return ctx
    


# Write Review 
class ReviewCreate(LoginRequiredMixin, generic.View):
    template_name = "polls/review_form.html"

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ReviewForm()
        formset = ReviewMediaFormSet()
        return render(request, self.template_name, {"product": product, "form": form, "formset": formset})

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        form = ReviewForm(request.POST, request.FILES)
        formset = ReviewMediaFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            # save media
            formset.instance = review
            formset.save()
            # optional wear test
            if form.cleaned_data.get("start_wear_test"):
                WearTest.objects.create(review=review)
            messages.success(request, "Thanks! Your review has been posted.")
            return redirect("product-detail", pk=product.pk)
        return render(request, self.template_name, {"product": product, "form": form, "formset": formset})
    



# Review Helpfulness Voting
class ReviewHelpfulnessView(LoginRequiredMixin, generic.View):
    """Handle helpful/not helpful votes on reviews"""
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)
        is_helpful = request.POST.get('is_helpful') == 'true'
        
        # Get or create the helpfulness vote
        vote, created = ReviewHelpfulness.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )
        
        if not created:
            # Update existing vote
            vote.is_helpful = is_helpful
            vote.save()
        
        # Update review helpful votes count
        helpful_count = review.helpfulness_votes.filter(is_helpful=True).count()
        not_helpful_count = review.helpfulness_votes.filter(is_helpful=False).count()
        
        review.helpful_votes = helpful_count
        review.save()
        
        return redirect('product-detail', pk=review.product.pk)

# Wear Test Controls

# Enhanced Product Detail with Review Statistics
class ProductDetail(generic.DetailView):
    model = Product
    template_name = "polls/product_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get review statistics
        reviews = product.reviews.all()
        context.update({
            'reviews': reviews,
            'review_count': reviews.count(),
            'average_rating': product.average_rating,
            'rating_distribution': product.rating_distribution,
            'verified_reviews': reviews.filter(is_verified_purchase=True),
            'recent_reviews': reviews[:5],  # Last 5 reviews
        })
        
        # Check if user has already reviewed this product
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = reviews.filter(user=self.request.user).exists()
            context['user_review'] = reviews.filter(user=self.request.user).first()
        
        return context

# Review List with Filtering
class ReviewListView(generic.ListView):
    model = Review
    template_name = "polls/review_list.html"
    paginate_by = 10
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        if product_id:
            qs = Review.objects.filter(product_id=product_id)
        else:
            qs = Review.objects.all()
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating:
            qs = qs.filter(rating=rating)
        
        # Filter by verified purchase
        verified = self.request.GET.get('verified')
        if verified == 'true':
            qs = qs.filter(is_verified_purchase=True)
        
        # Filter by skin type
        skin_type = self.request.GET.get('skin_type')
        if skin_type:
            qs = qs.filter(skin_type=skin_type)
        
        # Sort options
        sort = self.request.GET.get('sort', 'newest')
        sort_map = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'highest_rating': '-rating',
            'lowest_rating': 'rating',
            'most_helpful': '-helpful_votes',
        }
        
        return qs.order_by(sort_map.get(sort, '-created_at'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'product_id': self.kwargs.get('product_id'),
            'rating_choices': [(i, f'{i} star{"s" if i != 1 else ""}') for i in range(1, 6)],
            'skin_type_choices': [
                ('oily', 'Oily'),
                ('dry', 'Dry'),
                ('combination', 'Combination'),
                ('sensitive', 'Sensitive'),
                ('normal', 'Normal'),
            ],
        })
        return context

# Sign Up
class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm      
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        next_url = self.request.POST.get("next") or self.request.GET.get("next") or reverse("product-list")
        return redirect(next_url)

# User Profile
class UserProfileView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "polls/user_profile.html"
    context_object_name = "reviews"
    paginate_by = 10
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['total_reviews'] = Review.objects.filter(user=user).count()
        context['average_rating'] = Review.objects.filter(user=user).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
        return context

# Custom Logout View
class CustomLogoutView(generic.View):
    def post(self, request):
        logout(request)
        return redirect('login')

# Missions Page
class MissionsView(LoginRequiredMixin, TemplateView):
    template_name = "polls/missions.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Mock data for missions (in a real app, this would come from a database)
        daily_missions = [
            {
                'id': 1,
                'title': 'Post a lipstick swatch in red',
                'description': 'Share a swatch of a red lipstick product',
                'points': 10,
                'progress': 2,
                'target': 1,
                'completed': True,
                'icon': '💄'
            },
            {
                'id': 2,
                'title': 'Rate 3 products',
                'description': 'Rate at least 3 different products',
                'points': 15,
                'progress': 1,
                'target': 3,
                'completed': False,
                'icon': '⭐'
            },
            {
                'id': 3,
                'title': 'Write a detailed review',
                'description': 'Write a review with 200+ words',
                'points': 20,
                'progress': 0,
                'target': 1,
                'completed': False,
                'icon': '✍️'
            }
        ]
        
        weekly_missions = [
            {
                'id': 4,
                'title': 'Review a product under $20',
                'description': 'Find and review an affordable product',
                'points': 25,
                'progress': 0,
                'target': 1,
                'completed': False,
                'icon': '💰'
            },
            {
                'id': 5,
                'title': 'Upload 5 wear test photos',
                'description': 'Share photos showing product wear throughout the day',
                'points': 50,
                'progress': 3,
                'target': 5,
                'completed': False,
                'icon': '📸'
            },
            {
                'id': 6,
                'title': 'Discover 10 new products',
                'description': 'Browse and explore new products in the catalog',
                'points': 30,
                'progress': 7,
                'target': 10,
                'completed': False,
                'icon': '🔍'
            }
        ]
        
        # Mock badges data
        badges = [
            {
                'id': 1,
                'name': 'Foundation Explorer',
                'description': 'Reviewed 10 foundations',
                'icon': '🏆',
                'earned': True,
                'color': 'gold'
            },
            {
                'id': 2,
                'name': 'Lipstick Legend',
                'description': 'Expert in lip products',
                'icon': '💋',
                'earned': True,
                'color': 'red'
            },
            {
                'id': 3,
                'name': 'Review Rockstar',
                'description': 'Write 50 reviews',
                'icon': '⭐',
                'earned': False,
                'color': 'purple'
            }
        ]
        
        # Mock leaderboard data
        leaderboard = [
            {'rank': 1, 'username': 'GQ GlamQueen', 'points': 120, 'avatar': 'GQ', 'crown': True},
            {'rank': 2, 'username': 'ST ShadeTwin', 'points': 90, 'avatar': 'ST', 'crown': False},
            {'rank': 3, 'username': 'MM MakeupMaven', 'points': 85, 'avatar': 'MM', 'crown': False},
            {'rank': 4, 'username': 'BB BeautyBoss', 'points': 78, 'avatar': 'BB', 'crown': False},
            {'rank': 5, 'username': 'You', 'points': 65, 'avatar': user.username[:2].upper(), 'crown': False, 'is_current_user': True}
        ]
        
        # Calculate user stats
        total_points = sum([mission['points'] for mission in daily_missions + weekly_missions if mission['completed']])
        earned_badges = len([badge for badge in badges if badge['earned']])
        
        context.update({
            'daily_missions': daily_missions,
            'weekly_missions': weekly_missions,
            'badges': badges,
            'leaderboard': leaderboard,
            'total_points': total_points,
            'earned_badges': earned_badges,
            'user': user
        })
        
        return context