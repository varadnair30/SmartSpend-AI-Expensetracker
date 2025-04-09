# userpreferences/context_processors.py

from .models import UserPreference
from utils.vite_assets import get_vite_asset

CURRENCY_SYMBOLS = {
    'USD': '$',
    'INR': '₹',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'C$',
    'AUD': 'A$',
    'CHF': 'Fr',
    'CNY': '¥',
    'SGD': 'S$',
    # Add more as needed
}

def currency_processor(request):
    currency_code = 'USD'  # default fallback
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)

    if request.user.is_authenticated:
        try:
            pref = UserPreference.objects.get(user=request.user)
            if pref.currency:
                currency_code = pref.currency.split(' - ')[0]
                symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
        except UserPreference.DoesNotExist:
            pass

    return {
        'currency': symbol,
        'currency_code': currency_code
    }

def vite_manifest(request):
    assets = get_vite_asset('src/main.jsx')
    return {
        'vite_js': assets['js'],
        'vite_css': assets['css']
    }
