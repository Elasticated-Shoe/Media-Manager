from flask import render_template
import protected.globals as shared

@shared.cache.cached(key_prefix='dashboard') # Decorator caches the dashboard html PERMANENTLY
def renderDashboard():
    print("Cache Not Used")
    return render_template('dashboard.html', pageHead="Dashboard")