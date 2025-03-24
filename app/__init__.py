import os
from flask import Flask
from .db.connection import init_db, close_db
from .routes import conversations, messages, api
from .utils.filters import register_filters

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'athena.db'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    init_db(app)
    app.teardown_appcontext(close_db)

    # Register blueprints
    app.register_blueprint(conversations.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(api.bp)

    # Register custom filters
    register_filters(app)

    return app 