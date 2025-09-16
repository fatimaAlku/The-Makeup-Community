from django.conf import settings
from django.conf.urls.static import static


from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductList.as_view(), name="product-list"),
    path("products/", views.ProductBrowse.as_view(), name="products"),
    path("products/new/", views.ProductCreate.as_view(), name="product-create"),
    path("products/<int:pk>/", views.ProductDetail.as_view(), name="product-detail"),
    path("products/<int:pk>/edit/", views.ProductUpdate.as_view(), name="product-update"),
    path("products/<int:pk>/delete/", views.ProductDelete.as_view(), name="product-delete"),

    path("products/<int:product_id>/reviews/new/", views.ReviewCreate.as_view(), name="review-create"),
    path("products/<int:product_id>/reviews/", views.ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:review_id>/helpful/", views.ReviewHelpfulnessView.as_view(), name="review-helpful"),

    path("reviews/<int:pk>/edit/", views.ReviewUpdate.as_view(), name="review-update"),
    path("reviews/<int:pk>/delete/", views.ReviewDelete.as_view(), name="review-delete"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("missions/", views.MissionsView.as_view(), name="missions"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("trends/", views.TrendsView.as_view(), name="trends"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)