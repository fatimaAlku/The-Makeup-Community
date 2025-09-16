#!/usr/bin/env python
"""
Update existing products with new image URLs
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
import django
django.setup()

from polls.models import Product

# Update existing products with new image URLs
products_to_update = [
    ('Fenty Beauty', 'Stunna Lip Paint in Uncensored', '/static/img/products/fenty beauty Stunna lip paint in uncensored.jpg'),
    ('Rare Beauty', 'Liquid Lipstick in Brave', '/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif'),
    ('Glossier', 'Generation G Matte Lipstick in Cake', '/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif'),
    ('Charlotte Tilbury', 'Pillow Talk Lipstick', '/static/img/products/luxe beauty velvet matte lipstick in ruby red.avif'),
    ('Anastasia Beverly Hills', 'Modern Renaissance Palette', '/static/img/products/color dreams sunset eyeshadow palette.webp'),
    ('Urban Decay', 'Naked Heat Eyeshadow Palette', '/static/img/products/color dreams sunset eyeshadow palette.webp'),
    ('Huda Beauty', 'Desert Dusk Eyeshadow Palette', '/static/img/products/color dreams sunset eyeshadow palette.webp'),
    ('Morphe', '35O2 Second Nature Eyeshadow Palette', '/static/img/products/color dreams sunset eyeshadow palette.webp'),
    ('Too Faced', 'Better Than Sex Mascara', '/static/img/products/lash paradise mascara loreal.avif'),
    ('Benefit Cosmetics', "They're Real! Mascara", '/static/img/products/lash paradise mascara loreal.avif'),
    ('L\'Oréal', 'Lash Paradise Mascara', '/static/img/products/lash paradise mascara loreal.avif'),
    ('Maybelline', 'Sky High Mascara', '/static/img/products/lash paradise mascara loreal.avif'),
    ('Rare Beauty', 'Soft Pinch Liquid Blush', '/static/img/products/rare beauty soft pinch liquid blush.webp'),
    ('Fenty Beauty', 'Cheeks Out Freestyle Cream Blush', '/static/img/products/rare beauty soft pinch liquid blush.webp'),
    ('Glossier', 'Cloud Paint in Puff', '/static/img/products/rare beauty soft pinch liquid blush.webp'),
]

updated_count = 0
for brand, name, image_url in products_to_update:
    try:
        product = Product.objects.get(brand=brand, name=name)
        product.image_url = image_url
        product.save()
        updated_count += 1
        print(f'✅ Updated: {brand} - {name}')
    except Product.DoesNotExist:
        print(f'❌ Not found: {brand} - {name}')

print(f'\n🎉 Successfully updated {updated_count} products with new image URLs!')
