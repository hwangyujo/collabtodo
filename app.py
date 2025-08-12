from flask import Flask
from extensions import db, bcrypt, login_manager, socketio

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_here'  # 실제 배포 시 변경
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collabtodo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User
    from routes.auth_routes import auth_bp
    from routes.todo_routes import todo_bp
    from routes.friend_routes import friend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(friend_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host="127.0.0.1", port=5000
