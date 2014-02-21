"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'home', view_func=views.home)

# merchants list page
app.add_url_rule('/results', 'list_results', view_func=views.list_results, methods=['GET'])

# merchants list page
app.add_url_rule('/grab', 'grab', view_func=views.grab, methods=['GET'])

# merchants list page
app.add_url_rule('/merchants', 'list_merchants', view_func=views.list_merchants, methods=['GET', 'POST'])

# merchants list page (cached)
app.add_url_rule('/merchants/cached', 'cached_merchants', view_func=views.cached_merchants, methods=['GET'])

# Contrived admin-only view merchant
app.add_url_rule('/admin_only', 'admin_only', view_func=views.admin_only)

# Edit an merchant
app.add_url_rule('/merchants/<int:merchant_id>/edit', 'edit_merchant', view_func=views.edit_merchant, methods=['GET', 'POST'])

# Delete an merchant
app.add_url_rule('/merchants/<int:merchant_id>/delete', view_func=views.delete_merchant, methods=['POST'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

