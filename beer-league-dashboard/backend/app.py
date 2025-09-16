from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api
from config import config
from database import init_db
from services.data_loader import DataLoaderService
import os

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize Flask-RESTX
    api = Api(
        app,
        version=app.config['API_VERSION'],
        title=app.config['API_TITLE'],
        description=app.config['API_DESCRIPTION'],
        doc='/docs/'
    )
    
    # Initialize database
    init_db()
    
    # Register API namespaces
    from api.standings import api as standings_ns
    from api.matchups import api as matchups_ns
    from api.analytics import api as analytics_ns
    
    api.add_namespace(standings_ns, path='/api/standings')
    api.add_namespace(matchups_ns, path='/api/matchups')
    api.add_namespace(analytics_ns, path='/api/analytics')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': app.config['API_VERSION'],
            'environment': config_name
        })
    
    # Data sync endpoint
    @app.route('/api/sync')
    def sync_data():
        try:
            loader = DataLoaderService(app.config['DATA_DIR'])
            results = loader.sync_database()
            return jsonify({
                'status': 'success',
                'message': 'Data synchronized successfully',
                'results': results
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=3000, debug=True)
