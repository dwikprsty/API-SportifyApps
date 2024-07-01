from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import jwt  # Assuming jwt is your JWTManager instance
from auth.auth import auth_bp
from apisportify.lapangan import lapangan_bp
from apisportify.user import user_bp
from apisportify.reservasi import reservasi_bp
from apisportify.static_file_server import static_file_server
from config import Config

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

jwt.init_app(app)  # Initialize JWTManager here

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(lapangan_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(reservasi_bp, url_prefix='/api')
app.register_blueprint(static_file_server, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
