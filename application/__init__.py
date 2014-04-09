"""
Initialize Flask app

"""
from flask import Flask
import os
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication
from flask.ext.openid import OpenID
from openid.extensions import pape

from flask.ext.login import LoginManager

app = Flask('application')
# login_manager = LoginManager()
# login_manager.init_app(app)

oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])


if os.getenv('FLASK_CONF') == 'DEV':
    #development settings n
    app.config.from_object('application.settings.Development')
    # Flask-DebugToolbar (only enabled when DEBUG=True)
    toolbar = DebugToolbarExtension(app)

    # Google app engine mini profiler
    # https://github.com/kamens/gae_mini_profiler
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    from gae_mini_profiler import profiler, templatetags

    @app.context_processor
    def inject_profiler():
        return dict(profiler_includes=templatetags.profiler_includes())

    app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)

elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('application.settings.Testing')

else:
    app.config.from_object('application.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Pull in URL dispatch routes
import urls


