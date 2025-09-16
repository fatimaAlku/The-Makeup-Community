#!/usr/bin/env python
"""
Idempotent seeder for The Makeup Community (Django).
- Creates demo users with known passwords
- Creates mock products (with images)
- Creates random reviews per product (one per user)

Run:  python seed.py
"""

import os
import random
from datetime import timedelta
from django.utils import timezone

# --- Django setup ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django  # noqa: E402
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from polls.models import Product, Review  # noqa: E402

User = get_user_model()

DEMO_PASSWORD = "demo12345"  # login password for all demo users

USERS = [
    {"username": "aria", "email": "aria@example.com"},
    {"username": "ben", "email": "ben@example.com"},
    {"username": "cami", "email": "cami@example.com"},
    {"username": "diego", "email": "diego@example.com"},
    {"username": "fatima", "email": "fatima@example.com"},
    {"username": "sophia", "email": "sophia@example.com"},
    {"username": "maya", "email": "maya@example.com"},
    {"username": "zoe", "email": "zoe@example.com"},
    {"username": "luna", "email": "luna@example.com"},
    {"username": "chloe", "email": "chloe@example.com"},
    {"username": "emma", "email": "emma@example.com"},
    {"username": "olivia", "email": "olivia@example.com"},
    {"username": "ava", "email": "ava@example.com"},
    {"username": "isabella", "email": "isabella@example.com"},
    {"username": "mia", "email": "mia@example.com"},
    {"username": "charlotte", "email": "charlotte@example.com"},
    {"username": "amelia", "email": "amelia@example.com"},
    {"username": "harper", "email": "harper@example.com"},
    {"username": "evelyn", "email": "evelyn@example.com"},
    {"username": "abigail", "email": "abigail@example.com"},
]

PRODUCTS = [
    # Trending Lip Products
    {
        "brand": "Fenty Beauty",
        "name": "Stunna Lip Paint in Uncensored",
        "category": "lipstick",
        "price": 25,
        "image_url": "/static/img/products/fenty beauty Stunna lip paint in uncensored.jpg",
    },
    {
        "brand": "Rare Beauty",
        "name": "Liquid Lipstick in Brave",
        "category": "lipstick",
        "price": 22,
        "image_url": "/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif",
    },
    {
        "brand": "Glossier",
        "name": "Generation G Matte Lipstick in Cake",
        "category": "lipstick",
        "price": 18,
        "image_url": "/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif",
    },
    {
        "brand": "Charlotte Tilbury",
        "name": "Pillow Talk Lipstick",
        "category": "lipstick",
        "price": 35,
        "image_url": "/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif",
    },
    
    # Trending Foundation & Base
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Soft Matte Foundation",
        "category": "foundation",
        "price": 38,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Rare Beauty",
        "name": "Liquid Touch Weightless Foundation",
        "category": "foundation",
        "price": 29,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "NARS",
        "name": "Light Reflecting Foundation",
        "category": "foundation",
        "price": 50,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Glossier",
        "name": "Perfecting Skin Tint",
        "category": "foundation",
        "price": 26,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    
    # Trending Eyeshadow Palettes
    {
        "brand": "Anastasia Beverly Hills",
        "name": "Modern Renaissance Palette",
        "category": "eyeshadow",
        "price": 45,
        "image_url": "/static/img/products/color dreams sunset eyeshadow palette.webp",
    },
    {
        "brand": "Urban Decay",
        "name": "Naked Heat Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 54,
        "image_url": "/static/img/products/color dreams sunset eyeshadow palette.webp",
    },
    {
        "brand": "Huda Beauty",
        "name": "Desert Dusk Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 65,
        "image_url": "/static/img/products/color dreams sunset eyeshadow palette.webp",
    },
    {
        "brand": "Morphe",
        "name": "35O2 Second Nature Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 25,
        "image_url": "/static/img/products/color dreams sunset eyeshadow palette.webp",
    },
    
    # Trending Mascara & Lashes
    {
        "brand": "Too Faced",
        "name": "Better Than Sex Mascara",
        "category": "mascara",
        "price": 26,
        "image_url": "/static/img/products/lash paradise mascara loreal.avif",
    },
    {
        "brand": "Benefit Cosmetics",
        "name": "They're Real! Mascara",
        "category": "mascara",
        "price": 25,
        "image_url": "/static/img/products/lash paradise mascara loreal.avif",
    },
    {
        "brand": "L'Oréal",
        "name": "Lash Paradise Mascara",
        "category": "mascara",
        "price": 12,
        "image_url": "/static/img/products/lash paradise mascara loreal.avif",
    },
    {
        "brand": "Maybelline",
        "name": "Sky High Mascara",
        "category": "mascara",
        "price": 9,
        "image_url": "/static/img/products/lash paradise mascara loreal.avif",
    },
    
    # Trending Concealer & Corrector
    {
        "brand": "Tarte",
        "name": "Shape Tape Concealer",
        "category": "concealer",
        "price": 27,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "NARS",
        "name": "Radiant Creamy Concealer",
        "category": "concealer",
        "price": 32,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Instant Retouch Concealer",
        "category": "concealer",
        "price": 25,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    
    # Trending Blush & Highlighter
    {
        "brand": "Rare Beauty",
        "name": "Soft Pinch Liquid Blush",
        "category": "blush",
        "price": 20,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Cheeks Out Freestyle Cream Blush",
        "category": "blush",
        "price": 22,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Glossier",
        "name": "Cloud Paint in Puff",
        "category": "blush",
        "price": 18,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Killawatt Freestyle Highlighter",
        "category": "highlighter",
        "price": 38,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    
    # Trending Skincare-Makeup Hybrids
    {
        "brand": "Glossier",
        "name": "Futuredew Oil-Serum Hybrid",
        "category": "skincare",
        "price": 24,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Rare Beauty",
        "name": "Always an Optimist 4-in-1 Prime & Set Mist",
        "category": "skincare",
        "price": 22,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Instant Retouch Setting Powder",
        "category": "powder",
        "price": 32,
        "image_url": "/static/img/products/rare beauty soft pinch liquid blush.webp",
    },
]

REVIEW_SNIPPETS = [
    # Positive Reviews
    "Absolutely love this! The formula is incredible and lasts all day.",
    "This is my holy grail product. Perfect for my skin type.",
    "Amazing pigmentation and blendability. Worth every penny!",
    "I've been using this for months and it's still my go-to.",
    "The color payoff is stunning and it doesn't budge all day.",
    "Perfect for my oily skin - no creasing or fading.",
    "This gives me the perfect natural look I've been searching for.",
    "The texture is so smooth and applies like a dream.",
    "I get so many compliments when I wear this!",
    "This product has completely changed my makeup routine.",
    "The staying power is incredible - 12+ hours easily.",
    "Love how buildable this is - can go from subtle to dramatic.",
    "This is exactly what I was looking for. Highly recommend!",
    "The finish is flawless and looks expensive.",
    "I've tried so many similar products and this is the best.",
    "Perfect for beginners - so easy to work with.",
    "This gives me that Instagram-worthy glow every time.",
    "The packaging is beautiful and the product inside is even better.",
    "I can't believe how good this looks on my skin tone.",
    "This has become a staple in my everyday routine.",
    
    # Mixed Reviews
    "Good product overall, but the price is a bit steep.",
    "Nice formula, but the shade range could be better.",
    "Works well, though it takes some practice to apply correctly.",
    "Decent quality, but there are cheaper alternatives that work just as well.",
    "I like it, but it's not quite what I expected from the reviews.",
    "Good for special occasions, but too heavy for everyday wear.",
    "Nice color, but the staying power could be better.",
    "It's okay, but I probably won't repurchase.",
    "Good product, but the packaging could be more travel-friendly.",
    "Decent quality, but the application takes longer than I'd like.",
    
    # Critical Reviews
    "Not worth the hype. Doesn't work well with my skin type.",
    "The formula is too thick and hard to blend.",
    "Color doesn't match what I expected from the swatches.",
    "This product doesn't last as long as advertised.",
    "Too expensive for what you get. Disappointed.",
    "The packaging broke after just a few uses.",
    "This caused a reaction on my sensitive skin.",
    "The color payoff is much weaker than expected.",
    "Not suitable for my skin tone despite the claims.",
    "This product doesn't work well in humid weather.",
]

def create_users():
    print("→ Seeding users…")
    created_any = False
    for u in USERS:
        user, created = User.objects.get_or_create(username=u["username"], defaults={"email": u["email"]})
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
            print(f"  ✅ Created user: {user.username}")
            created_any = True
        else:
            # ensure password is set to known demo (optional)
            if not user.has_usable_password():
                user.set_password(DEMO_PASSWORD)
                user.save()
            print(f"  ⚠️  Exists: {user.username}")
    if not created_any:
        print("  (no new users)")

def create_products():
    print("→ Seeding products…")
    for p in PRODUCTS:
        obj, created = Product.objects.get_or_create(
            name=p["name"],
            defaults=p
        )
        msg = "✅ Created" if created else "⚠️  Exists"
        print(f"  {msg}: {obj}")

def create_reviews():
    print("→ Seeding reviews…")
    users = list(User.objects.filter(username__in=[u["username"] for u in USERS]))
    if not users:
        print("  No users found, skipping reviews.")
        return
    products = list(Product.objects.all())
    for prod in products:
        # each user writes at most one review per product
        for user in users:
            if Review.objects.filter(user=user, product=prod).exists():
                continue
            rating = random.randint(1, 5)  # full range of ratings for realistic reviews
            title = random.choice([
                # 5-star titles
                "Absolutely perfect!", "Holy grail product!", "Worth every penny!", "Life-changing!", "Perfect match!",
                "My new favorite!", "Incredible quality!", "Flawless finish!", "Amazing results!", "Love it!",
                
                # 4-star titles
                "Really great product", "Solid choice", "Pretty impressed", "Would recommend", "Good quality",
                "Nice formula", "Works well", "Happy with purchase", "Good value", "Satisfied",
                
                # 3-star titles
                "It's okay", "Decent product", "Not bad", "Average quality", "Could be better",
                "Mixed feelings", "So-so", "Alright", "Fair", "Meh",
                
                # 2-star titles
                "Disappointed", "Not what I expected", "Could be improved", "Below average", "Not great",
                "Had issues", "Not impressed", "Won't repurchase", "Overpriced", "Not worth it",
                
                # 1-star titles
                "Terrible", "Waste of money", "Awful quality", "Don't buy", "Regret purchase",
                "Complete fail", "Horrible", "Worst product", "Avoid this", "Big mistake"
            ])
            body = random.choice(REVIEW_SNIPPETS)
            created_at = timezone.now() - timedelta(days=random.randint(0, 60))
            r = Review.objects.create(
                user=user, product=prod, title=title, body=body,
                rating=rating, is_verified_purchase=random.choice([True, False]),
                created_at=created_at, updated_at=created_at
            )
            print(f"  ✍️  {user.username} → {prod.name} ({rating}/5)")
    print("  done.")

def run():
    create_users()
    create_products()
    create_reviews()
    print("\n✅ Seeding complete.")

if __name__ == "__main__":
    run()

