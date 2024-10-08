from flask import Flask
from api.routes import api  # Import the Blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)  # Register the Blueprint with the app

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)