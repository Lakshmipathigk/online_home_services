from flask import send_from_directory
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import sys

app = Flask(__name__)
CORS(app)

basedir = os.getcwd()
db_path = os.path.join(basedir, 'services.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

@app.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{ 'id': s.id, 'name': s.name, 'description': s.description } for s in services])

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')


def main():
    try:
        with app.app_context():
            db.create_all()

            #  Add this part to insert dummy services if the table is empty
            if Service.query.count() == 0:
                db.session.add(Service(name='Plumbing', description='Fixing leaks and pipes'))
                db.session.add(Service(name='Electrician', description='Electrical repair and installation'))
                db.session.commit()

        app.run(host='127.0.0.1', port=5000, debug=True)

    except Exception as e:
        sys.stderr.write(f"Failed to start Flask app: {e}\n")
        return

if __name__ == '__main__':
    main()
