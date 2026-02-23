from decimal import Decimal
from django.contrib.auth.models import User
from myapp.models import Product

# Seller selection: try username 'f', then any staff user, otherwise create 'seed_seller'
seller = None
try:
    seller = User.objects.get(username='f')
except User.DoesNotExist:
    seller = User.objects.filter(is_staff=True).first()

if not seller:
    seller, created = User.objects.get_or_create(
        username='seed_seller',
        defaults={'email': 'seed_seller@example.com'}
    )
    if created:
        seller.set_password('password')
        seller.is_staff = True
        seller.save()

products = [
    # Tech (10 total)
    {'title': 'Motorola Galaxy Z TriFold', 'brand': 'Motorola', 'price': Decimal('1800.00'), 'description': 'A three-panel folding phone that expands into a full 12-inch tablet.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/motorola_trifold/800/600', 'stock_count': 5},
    {'title': 'Roborock Saros Rover', 'brand': 'Roborock', 'price': Decimal('1200.00'), 'description': 'Stair-climbing robot vacuum designed for multi-level homes.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/roborock_saros/800/600', 'stock_count': 8},
    {'title': 'Xreal 1S AR Glasses', 'brand': 'Xreal', 'price': Decimal('450.00'), 'description': '700-nit portable private screen for immersive AR viewing.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/xreal_1s/800/600', 'stock_count': 12},
    {'title': 'Solos AirGo V2', 'brand': 'Solos', 'price': Decimal('250.00'), 'description': 'AI translation smart glasses for seamless conversation.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/solos_airgo/800/600', 'stock_count': 15},
    {'title': 'AuraCharge Wireless Lock', 'brand': 'AuraCharge', 'price': Decimal('120.00'), 'description': 'Optical charging smart lock with secure wireless power transfer.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/auracharge_lock/800/600', 'stock_count': 20},
    {'title': 'Allergen Alert Mini Lab', 'brand': 'Allergen', 'price': Decimal('95.00'), 'description': 'Portable food sensor for on-the-go allergen detection.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/allergen_mini_lab/800/600', 'stock_count': 25},
    {'title': 'NeuraSense Sleep Band', 'brand': 'NeuraSense', 'price': Decimal('149.99'), 'description': 'Wearable band that tracks sleep stages and offers gentle coaching.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/neuralsense_sleep/800/600', 'stock_count': 30},
    {'title': 'PocketLab Quantum Charger', 'brand': 'PocketLab', 'price': Decimal('79.99'), 'description': 'Compact fast wireless charger for multiple devices.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/pocketlab_charger/800/600', 'stock_count': 40},
    {'title': 'VegaHome Smart Display', 'brand': 'VegaHome', 'price': Decimal('219.99'), 'description': 'Smart home display with AI routines and crisp audio.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/vegahome_display/800/600', 'stock_count': 14},
    {'title': 'NanoBeam Portable SSD', 'brand': 'NanoBeam', 'price': Decimal('139.99'), 'description': 'Ultra-fast compact external SSD with durable casing.', 'category': 'tech', 'image_url': 'https://picsum.photos/seed/nanobeam_ssd/800/600', 'stock_count': 21},

    # Fashion (10 total)
    {'title': 'Relaxed Fit Raw Denim', 'brand': 'Patilcraft', 'price': Decimal('69.99'), 'description': 'Sustainable raw finish denim — relaxed fit for everyday wear. Target: Male. Budget segment.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/relaxed_raw_denim/800/600', 'stock_count': 30},
    {'title': 'Technical Windbreaker', 'brand': 'Patilcraft', 'price': Decimal('129.99'), 'description': 'Weather-proof activewear windbreaker with technical fabrics. Target: Male. Mid-Range.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/technical_windbreaker/800/600', 'stock_count': 18},
    {'title': 'Ribbed Knit Midi Skirt', 'brand': 'Patilcraft', 'price': Decimal('39.99'), 'description': 'Essentials daily wear ribbed knit midi skirt. Target: Female. Budget segment.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/ribbed_midi_skirt/800/600', 'stock_count': 40},
    {'title': 'Leather Knee-High Boots', 'brand': 'Patilcraft', 'price': Decimal('199.99'), 'description': 'Premium leather knee-high boots for elevated looks. Target: Female. Mid-Range.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/leather_knee_high_boots/800/600', 'stock_count': 10},
    {'title': 'Organic Cotton Play Suit', 'brand': 'Patilcraft', 'price': Decimal('35.99'), 'description': 'Eco-friendly organic cotton playsuit for kids. Target: Kids. Budget segment.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/organic_play_suit/800/600', 'stock_count': 22},
    {'title': 'Reversible Puffer Vest', 'brand': 'Patilcraft', 'price': Decimal('89.99'), 'description': 'Versatile reversible puffer vest for layering. Target: Kids. Mid-Range.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/reversible_puffer_vest/800/600', 'stock_count': 16},
    {'title': 'Performance Jogger', 'brand': 'Patilcraft', 'price': Decimal('49.99'), 'description': 'Lightweight joggers with moisture-wicking fabric. Target: Male. Budget segment.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/performance_jogger/800/600', 'stock_count': 26},
    {'title': 'Seamless Sports Bra', 'brand': 'Patilcraft', 'price': Decimal('29.99'), 'description': 'Comfort-first seamless sports bra for medium impact.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/seamless_sports_bra/800/600', 'stock_count': 34},
    {'title': 'Eco Linen Shirt', 'brand': 'Patilcraft', 'price': Decimal('59.99'), 'description': 'Breathable eco-linen shirt for warm weather comfort.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/eco_linen_shirt/800/600', 'stock_count': 20},
    {'title': 'Convertible Travel Jacket', 'brand': 'Patilcraft', 'price': Decimal('149.99'), 'description': 'Jacket converts to a packable travel pillow and tote.', 'category': 'fashion', 'image_url': 'https://picsum.photos/seed/convertible_travel_jacket/800/600', 'stock_count': 12},
]

for p in products:
    obj, created = Product.objects.update_or_create(
        title=p['title'],
        defaults={
            'seller': seller,
            'brand': p['brand'],
            'price': p['price'],
            'description': p['description'],
            'category': p['category'],
            'image_url': p['image_url'],
            'stock_count': p.get('stock_count', 10),
        }
    )
    if created:
        print(f"Created product: {obj.title}")
    else:
        print(f"Updated product: {obj.title}")

print('Seeding complete.')
