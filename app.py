from flask import Flask
from config import Config
from extensions import db

# Импорты blueprints
from blueprints.pages import pages_bp
from blueprints.groups import groups_bp
from blueprints.teachers import teachers_bp
from blueprints.subjects import subjects_bp
from blueprints.classrooms import classrooms_bp
from blueprints.lessons import lessons_bp
from blueprints.history import history_bp


def create_app():
    app = Flask(
        __name__,
        static_folder=Config.STATIC_FOLDER,
        template_folder=Config.TEMPLATE_FOLDER
    )
    app.config.from_object(Config)

    db.init_app(app)

    # Регистрация всех модулей
    app.register_blueprint(pages_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(classrooms_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(history_bp)

    with app.app_context():
        # Импортируем модели, чтобы SQLAlchemy их «увидел»
        import models  # noqa: F401
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)