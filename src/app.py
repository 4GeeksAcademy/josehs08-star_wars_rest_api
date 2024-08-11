"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorites
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def list_users():
    users = User.query.all()
    response = list(map(lambda x: x.serialize(), users))

    return jsonify(response), 200

@app.route('/populate', methods=['GET'])
def populate_db():
    response = requests.get('https://www.swapi.tech/api/people?page=1&limit=3')
    response = response.json()
    response = response.get('results')
    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result').get('properties')
        character = Character()
        character.height = result.get('height')
        character.hair_color = result.get('hair_color')
        character.skin_color = result.get('skin_color')
        character.eye_color = result.get('eye_color')
        character.birth_year = result.get('birth_year')
        character.gender = result.get('gender')
        character.name = result.get('name')
        db.session.add(character)
    try:
        db.session.commit()
        return jsonify({"msg": "DB populated successfully"}), 200
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500

@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    people_list = list()
    for people in people:
        people_list.append(people.serialize())
    return jsonify(people_list), 200

# POST FAVORITE CHARACTER
@app.route('/favorite/people/<int:people_id>')
def add_favorite(people_id):
    people = Character.query.filter_by(id=people_id).first()
    if people is None:
        return jsonify({"msg": "People not found"}), 404
    favorite = Favorites()
    favorite.character_id = people_id
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "People added to favorites"}), 201
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)