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
        "image_url": "/static/img/products/Fenty Beauty — Stunna Lip Paint in Uncensored.jpg",
    },
    {
        "brand": "Rare Beauty",
        "name": "Liquid Lipstick in Brave",
        "category": "lipstick",
        "price": 22,
        "image_url": "/static/img/products/Rare Beauty — Liquid Lipstick in Brave.webp",
    },
    {
        "brand": "Glossier",
        "name": "Generation G Matte Lipstick in Cake",
        "category": "lipstick",
        "price": 18,
        "image_url": "/static/img/products/Glossier — Generation G Matte Lipstick in Cake.png",
    },
    {
        "brand": "Charlotte Tilbury",
        "name": "Pillow Talk Lipstick",
        "category": "lipstick",
        "price": 35,
        "image_url": "/static/img/products/Charlotte Tilbury — Pillow Talk Lipstick.webp",
    },
    
    # Trending Foundation & Base
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Soft Matte Foundation",
        "category": "foundation",
        "price": 38,
        "image_url": "/static/img/products/Fenty Beauty — Pro Filt'r Soft Matte Foundation.webp",
    },
    {
        "brand": "Rare Beauty",
        "name": "Liquid Touch Weightless Foundation",
        "category": "foundation",
        "price": 29,
        "image_url": "/static/img/products/Rare Beauty — Liquid Touch Weightless Foundation.webp",
    },
    {
        "brand": "NARS",
        "name": "Light Reflecting Foundation",
        "category": "foundation",
        "price": 50,
        "image_url": "/static/img/products/NARS — Light Reflecting Foundation.avif",
    },
    {
        "brand": "Glossier",
        "name": "Perfecting Skin Tint",
        "category": "foundation",
        "price": 26,
        "image_url": "/static/img/products/Glossier — Perfecting Skin Tint.jpeg",
    },
    
    # Trending Eyeshadow Palettes
    {
        "brand": "Anastasia Beverly Hills",
        "name": "Modern Renaissance Palette",
        "category": "eyeshadow",
        "price": 45,
        "image_url": "/static/img/products/Anastasia Beverly Hills — Modern Renaissance Palette.jpg",
    },
    {
        "brand": "Urban Decay",
        "name": "Naked Heat Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 54,
        "image_url": "/static/img/products/Urban Decay — Naked Heat Eyeshadow Palette.jpg",
    },
    {
        "brand": "Huda Beauty",
        "name": "Desert Dusk Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 65,
        "image_url": "/static/img/products/Huda Beauty — Desert Dusk Eyeshadow Palette.avif",
    },
    {
        "brand": "Morphe",
        "name": "35O2 Second Nature Eyeshadow Palette",
        "category": "eyeshadow",
        "price": 25,
        "image_url": "/static/img/products/Morphe — 35O2 Second Nature Eyeshadow Palette.webp",
    },
    
    # Trending Mascara & Lashes
    {
        "brand": "Too Faced",
        "name": "Better Than Sex Mascara",
        "category": "mascara",
        "price": 26,
        "image_url": "/static/img/products/Too Faced — Better Than Sex Mascara.avif",
    },
    {
        "brand": "Benefit Cosmetics",
        "name": "They're Real! Mascara",
        "category": "mascara",
        "price": 25,
        "image_url": "/static/img/products/Benefit Cosmetics — They're Real! Mascara.avif",
    },
    {
        "brand": "L'Oréal",
        "name": "Lash Paradise Mascara",
        "category": "mascara",
        "price": 12,
        "image_url": "/static/img/products/L'Oréal — Lash Paradise Mascara.jpg",
    },
    {
        "brand": "Maybelline",
        "name": "Sky High Mascara",
        "category": "mascara",
        "price": 9,
        "image_url": "/static/img/products/Maybelline — Sky High Mascara.webp",
    },
    
    # Trending Concealer & Corrector
    {
        "brand": "Tarte",
        "name": "Shape Tape Concealer",
        "category": "concealer",
        "price": 27,
        "image_url": "/static/img/products/Tarte — Shape Tape Concealer.jpg",
    },
    {
        "brand": "NARS",
        "name": "Radiant Creamy Concealer",
        "category": "concealer",
        "price": 32,
        "image_url": "/static/img/products/NARS — Radiant Creamy Concealer.avif",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Instant Retouch Concealer",
        "category": "concealer",
        "price": 25,
        "image_url": "/static/img/products/Fenty Beauty — Pro Filt'r Instant Retouch Concealer.avif",
    },
    
    # Trending Blush & Highlighter
    {
        "brand": "Rare Beauty",
        "name": "Soft Pinch Liquid Blush",
        "category": "blush",
        "price": 20,
        "image_url": "/static/img/products/Rare Beauty — Soft Pinch Liquid Blush.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Cheeks Out Freestyle Cream Blush",
        "category": "blush",
        "price": 22,
        "image_url": "/static/img/products/Fenty Beauty — Cheeks Out Freestyle Cream Blush.jpg",
    },
    {
        "brand": "Glossier",
        "name": "Cloud Paint in Puff",
        "category": "blush",
        "price": 18,
        "image_url": "/static/img/products/Glossier — Cloud Paint in Puff.jpg",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Killawatt Freestyle Highlighter",
        "category": "highlighter",
        "price": 38,
        "image_url": "/static/img/products/Fenty Beauty — Killawatt Freestyle Highlighter.webp",
    },
    
    # Trending Skincare-Makeup Hybrids
    {
        "brand": "Glossier",
        "name": "Futuredew Oil-Serum Hybrid",
        "category": "skincare",
        "price": 24,
        "image_url": "/static/img/products/Glossier — Futuredew Oil-Serum Hybrid.png",
    },
    {
        "brand": "Rare Beauty",
        "name": "Always an Optimist 4-in-1 Prime & Set Mist",
        "category": "skincare",
        "price": 22,
        "image_url": "/static/img/products/Rare Beauty — Always an Optimist 4-in-1 Prime & Set Mist.webp",
    },
    {
        "brand": "Fenty Beauty",
        "name": "Pro Filt'r Instant Retouch Setting Powder",
        "category": "powder",
        "price": 32,
        "image_url": "/static/img/products/Fenty Beauty — Pro Filt'r Instant Retouch Setting Powder.jpg",
    },
    
    # --- New additions ---
    {
        "brand": "Kylie Cosmetics",
        "name": "Matte Liquid Lipstick “Candy K”",
        "category": "lipstick",
        "price": 18,
        "image_url": "/static/img/products/Kylie Cosmetics — Matte Liquid Lipstick “Candy K”.jpg",
    },
    {
        "brand": "Kylie Cosmetics",
        "name": "Velvet Lip Kit “Bare”",
        "category": "lipstick",
        "price": 29,
        "image_url": "/static/img/products/Kylie Cosmetics — Velvet Lip Kit “Bare”.jpg",
    },
    {
        "brand": "Kylie Cosmetics",
        "name": "Kylash Volume Mascara",
        "category": "mascara",
        "price": 24,
        "image_url": "/static/img/products/Kylie Cosmetics — Kylash Volume Mascara.webp",
    },
    {
        "brand": "Kylie Cosmetics",
        "name": "Pressed Blush Powder “Baddie on the Block”",
        "category": "blush",
        "price": 20,
        "image_url": "/static/img/products/Kylie Cosmetics — Pressed Blush Powder “Baddie on the Block”.avif",
    },
    {
        "brand": "Huda Beauty",
        "name": "Power Bullet Matte Lipstick “Interview”",
        "category": "lipstick",
        "price": 27,
        "image_url": "/static/img/products/Huda Beauty — Power Bullet Matte Lipstick “Interview”.jpg",
    },
    {
        "brand": "Huda Beauty",
        "name": "FauxFilter Luminous Matte Foundation",
        "category": "foundation",
        "price": 42,
        "image_url": "/static/img/products/Huda Beauty — FauxFilter Luminous Matte Foundation.jpg",
    },
    {
        "brand": "Huda Beauty",
        "name": "Easy Bake Loose Baking & Setting Powder",
        "category": "powder",
        "price": 35,
        "image_url": "/static/img/products/Huda Beauty — Easy Bake Loose Baking & Setting Powder.jpg",
    },
    {
        "brand": "Huda Beauty",
        "name": "Legit Lashes Double-Ended Mascara",
        "category": "mascara",
        "price": 27,
        "image_url": "/static/img/products/Huda Beauty — Legit Lashes Double-Ended Mascara.webp",
    },
    {
        "brand": "Summer Fridays",
        "name": "Lip Butter Balm “Vanilla”",
        "category": "skincare",
        "price": 24,
        "image_url": "/static/img/products/Summer Fridays — Lip Butter Balm “Vanilla”.webp",
    },
    {
        "brand": "Summer Fridays",
        "name": "Jet Lag Mask",
        "category": "skincare",
        "price": 49,
        "image_url": "/static/img/products/Summer Fridays — Jet Lag Mask.jpg",
    },
    {
        "brand": "NARS",
        "name": "Buttermelt Blush",
        "category": "blush",
        "price": 34,
        "image_url": "/static/img/products/Nars - Buttermelt Blush.jpg",
    },
]

POSITIVE_SNIPPETS = [
    "Absolutely love this! The formula is incredible and lasts all day.",
    "This is my holy grail product. Perfect for my skin type.",
    "Amazing pigmentation and blendability. Worth every penny!",
    "I've been using this for months and it's still my go-to.",
    "The color payoff is stunning and it doesn't budge all day.",
    "Perfect for my oily skin - no creasing or fading.",
    "The texture is so smooth and applies like a dream.",
    "Love how buildable this is - can go from subtle to dramatic.",
    "The finish is flawless and looks expensive.",
    "I've tried so many similar products and this is the best.",
]

MIXED_SNIPPETS = [
    "Good product overall, but the price is a bit steep.",
    "Nice formula, but the shade range could be better.",
    "Works well, though it takes some practice to apply correctly.",
    "I like it, but it's not quite what I expected from the reviews.",
    "Nice color, but the staying power could be better.",
    "Good product, but the packaging could be more travel-friendly.",
]

CRITICAL_SNIPPETS = [
    "Not worth the hype. Doesn't work well with my skin type.",
    "The formula is too thick and hard to blend.",
    "Color doesn't match what I expected from the swatches.",
    "This product doesn't last as long as advertised.",
    "Too expensive for what you get. Disappointed.",
    "The packaging broke after just a few uses.",
]

TITLES_BY_RATING = {
    5: [
        "Absolutely perfect!", "Holy grail product!", "Worth every penny!",
        "Life-changing!", "My new favorite!", "Incredible quality!",
    ],
    4: [
        "Really great product", "Solid choice", "Would recommend", "Good quality",
    ],
    3: [
        "It's okay", "Decent product", "Average quality", "Mixed feelings",
    ],
    2: [
        "Disappointed", "Not what I expected", "Below average", "Not great",
    ],
    1: [
        "Terrible", "Waste of money", "Awful quality", "Regret purchase",
    ],
}

def pick_snippet_for_rating(r: int) -> str:
    if r >= 5:
        pool = POSITIVE_SNIPPETS
    elif r == 4:
        pool = POSITIVE_SNIPPETS + MIXED_SNIPPETS
    elif r == 3:
        pool = MIXED_SNIPPETS
    elif r == 2:
        pool = MIXED_SNIPPETS + CRITICAL_SNIPPETS
    else:
        pool = CRITICAL_SNIPPETS
    return random.choice(pool)

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
        if created:
            print(f"  ✅ Created: {obj}")
        else:
            # Ensure existing records get the latest brand/category/price/image_url
            updated = False
            for field in ["brand", "category", "price", "image_url"]:
                new_val = p[field]
                if getattr(obj, field) != new_val:
                    setattr(obj, field, new_val)
                    updated = True
            if updated:
                obj.save(update_fields=["brand", "category", "price", "image_url"])
                print(f"  🔄 Updated: {obj}")
            else:
                print(f"  ⚠️  Exists (no changes): {obj}")

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
            # Bias ratings around 3–4 to look more realistic overall
            rating = random.choices([1,2,3,4,5], weights=[8,14,28,32,18], k=1)[0]
            title = random.choice(TITLES_BY_RATING[rating])
            body = pick_snippet_for_rating(rating)
            created_at = timezone.now() - timedelta(days=random.randint(0, 60))
            r = Review.objects.create(
                user=user, product=prod, title=title, body=body,
                rating=rating, is_verified_purchase=random.choice([True, False]),
                created_at=created_at, updated_at=created_at
            )
            print(f"  ✍️  {user.username} → {prod.name} ({rating}/5)")
    print("  done.")

def fix_existing_reviews():
    print("→ Normalizing existing reviews…")
    count = 0
    for r in Review.objects.all().only("id", "rating", "title", "body"):
        # Keep the stored star rating, refresh title/body to match tone
        rating = int(max(1, min(5, r.rating or 3)))
        new_title = random.choice(TITLES_BY_RATING.get(rating, TITLES_BY_RATING[3]))
        new_body = pick_snippet_for_rating(rating)
        if r.title != new_title or r.body != new_body:
            r.title = new_title
            r.body = new_body
            r.save(update_fields=["title", "body"])
            count += 1
    print(f"  🔄 Updated {count} existing reviews")

def run():
    create_users()
    create_products()
    create_reviews()
    fix_existing_reviews()
    print("\n✅ Seeding complete.")

if __name__ == "__main__":
    run()

