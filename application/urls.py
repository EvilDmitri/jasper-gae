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
app.add_url_rule('/', 'test', view_func=views.test, methods=['GET'])

# Test Show Result
app.add_url_rule('/<int:result_id>', 'test_result', view_func=views.test_result, methods=['GET', 'POST'])


# site selection page
app.add_url_rule('/sites', 'sites', view_func=views.sites, methods=['GET'])

# results list page
app.add_url_rule('/results', 'list_results', view_func=views.list_results, methods=['GET'])

# Show the merchant
app.add_url_rule('/result/<int:result_id>', 'show_result', view_func=views.show_result, methods=['GET', 'POST'])

# Delete a result
app.add_url_rule('/result/<int:result_id>/delete', view_func=views.delete_result, methods=['POST'])

# ajax grabber
app.add_url_rule('/grab', 'grab', view_func=views.grab, methods=['POST'])


# cron grabber
app.add_url_rule('/grabber/daily', 'grab_daily', view_func=views.grab_daily, methods=['GET'])

# merchants list page
# app.add_url_rule('/merchants', 'list_merchants', view_func=views.list_merchants, methods=['GET', 'POST'])

# merchants list page (cached)
# app.add_url_rule('/merchants/cached', 'cached_merchants', view_func=views.cached_merchants, methods=['GET'])

# Contrived admin-only view merchant
app.add_url_rule('/admin_only', 'admin_only', view_func=views.admin_only)





## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

