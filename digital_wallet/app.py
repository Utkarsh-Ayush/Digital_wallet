from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    
    @app.route('/')
    def index():
        return "Digital Wallet API is running"

    
    from routes.users import users_bp
    from routes.wallet import wallet_bp
    from routes.products import products_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(products_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
