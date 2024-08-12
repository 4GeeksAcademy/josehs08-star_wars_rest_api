import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorites
import requests

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

# GET ALL USER
@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    response = list(map(lambda x: x.serialize_fav(), users))
    return jsonify(response), 200

# POPULATE PEOPLE TABLE
@app.route('/populate', methods=['GET'])
def populate_db():
    response = requests.get('https://www.swapi.tech/api/people?page=1&limit=3')
    response = response.json()
    response = response.get('results')
    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result').get('properties')
        character = People()
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

# POPULATE PLANET TABLE
@app.route('/populateP', methods=['GET'])
def populateP():
    response = requests.get('https://www.swapi.tech/api/planets?page=1&limit=3')
    response = response.json()
    response = response.get('results')
    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result').get('properties')
        new_planet = Planet()
        new_planet.diameter=result.get('diameter')
        new_planet.rotation_period=result.get('rotation_period')
        new_planet.orbital_period=result.get('orbital_period')
        new_planet.gravity=result.get('gravity')
        new_planet.population=result.get('population')
        new_planet.climate=result.get('climate')
        new_planet.terrain=result.get('terrain')
        new_planet.surface_water=result.get('surface_water')
        new_planet.created_at=result.get('created')
        new_planet.name=result.get('name')
        new_planet.url=result.get('url')
        new_planet.description=result.get('description')
        db.session.add(new_planet)    
    try:
        db.session.commit()
        return jsonify({"msg": "DB populated successfully"}), 200
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500
    
# GET ALL PEOPLE
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = list(map(lambda x: x.serialize(), people))
    return jsonify(people_list), 200

# GET SINGLE PERSON
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    people = People.query.get(people_id)
    if not people:
        return jsonify({"msg": "Person not found"}),404
    else: 
        return jsonify(people.serialize()), 200

# GET ALL PLANETS
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = list(map(lambda x: x.serialize(), planets))
    return jsonify(planets_list), 200

# GET SINGLE PLANET
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}),404
    else: 
        return jsonify(planet.serialize()),200

# POST FAVORITE PEOPLE
@app.route('/favorite/people/<int:people_id>', methods =['POST'])
def add_favorite(people_id):
    response = request.get_json()
    user_id = response['user_id']
    favorite = Favorites()
    favorite.people_id = people_id
    favorite.user_id = user_id
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 201
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500

# POST FAVORITE PLANET
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    response = request.get_json()
    user_id = response['user_id']
    favorite = Favorites()
    favorite.planet_id = planet_id
    favorite.user_id = user_id
    db.session.add(favorite)
    try:
        db.session.commit()
        return jsonify({favorite}), 201
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500

# GET FAVORITES
@app.route('/users/favorites/', methods=['GET'])
def get_favorite():
    favorites = Favorites.query.all()
    response = list(map(lambda x:x.serialize_fav(),favorites))
    return jsonify(response),200

# DELETE FAVORITE CHARACTER
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite(people_id):
    favorite = Favorites.query.filter_by(people_id=people_id).first()
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Character deleted"}), 204
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500

# DELETE FAVORITE PLANET
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite = Favorites.query.filter_by(planet_id=planet_id).first()
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"msg": "Planet deleted"}), 204
    except Exception as error:
        print('ERROR:',error)
        db.session.rollback()
        return jsonify({"msg": "DB error"}), 500

# GET USER FAVORITES
@app.route('/users/favorites/<int:user_id>', methods = ['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    response = list(map(lambda x: x.serialize(),favorites))
    return jsonify(response),200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)