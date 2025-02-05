from flask import Flask
from config import Config
from models import db
from routes import main
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = b'\x9et,<\xeb\xd1\xcf\xde\xaf\xdb\x8fF;\x88\xf9\xb9\x1e]\x8a\xbeTg\x19\xb4'

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)