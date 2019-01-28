from flask import render_template
import protected.abstractions.globals as shared

@shared.cache.cached(key_prefix='notFound') # Decorator caches the dashboard html PERMANENTLY
def render404():
    print("404, Cache Not Used")
    return render_template('404.html', pageHead="Page Not Found")