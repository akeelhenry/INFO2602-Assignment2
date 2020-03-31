import json
from flask import Flask, request, render_template
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 

from models import db, MyPokemon, Pokemon, User

''' Begin boilerplate code '''
def create_app():
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = "MYSECRET"
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7) 
    db.init_app(app)
    return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''

''' Set up JWT here '''
def authenticate(uname, password):
    user = User.query.filter_by(username=uname).first()
    if user and user.check_password(password):
        return user

def identity(payload):
    return User.query.get(payload['identity'])

jwt = JWT(app, authenticate, identity)

''' End JWT Setup '''

#Query of first 50 pokemon objects and send to template to display
@app.route('/')
def index():
    pokemon = Pokemon.query.limit(50).all()
    return render_template('index.html',pokemon=pokemon)

@app.route('/app')
def client_app():
    return app.send_static_file('app.html')

#List of all pokemon in databse
@app.route('/pokemon', methods=['GET'])
def list_pokemon():
    pokemon_list = Pokemon.query.all()
    pokemon_list = [pokemon.toDict() for pokemon in pokemon_list]
    return json.dumps(pokemon_list),200

@app.route('/signup', methods=['POST'])
def signup():
    userdata = request.get_json()
    newuser = User(username=userdata['username'], email=userdata['email']) 
    newuser.set_password(userdata['password']) # set password
    try:
        db.session.add(newuser)
        db.session.commit() 
    except IntegrityError:
        db.session.rollback()
        return 'username or email already exists',409
    return 'user created',200

#Save/Catch Pokemon
@app.route('/mypokemon', methods=['POST'])
@jwt_required()
def save_pokemon():
    data = request.get_json()
    pokemon = MyPokemon(id=current_identity.id,pid=data['pid'],name=data['name'])
    db.session.add(pokemon)
    db.session.commit()
    return data['name'] + ' captured',201

#List all Pokemon caught by a user
@app.route('/mypokemon', methods=['GET'])
@jwt_required()
def list_my_pokemon():
    pokemon_list = MyPokemon.query.filter_by(id=current_identity.id)
    pokemon_list = [pokemon.toDict() for pokemon in pokemon_list]
    return json.dumps(pokemon_list),200

#Get specific Pokemon caught by a user user
@app.route('/mypokemon/<id>', methods=['GET'])
@jwt_required()
def get_pokemon(id):
    pokemon = MyPokemon.query.filter_by(id=current_identity.id)
    if pokemon.count() == 0:
        return 'No Pokemon captured!'
    try:
        pokemon = MyPokemon.query.filter_by(id=current_identity.id)[int(id)-1]
        return json.dumps(pokemon.toDict())
    except:
        return 'Invalid id or unauthorized'

#Update the name of a Pokemon caught by a user
@app.route('/mypokemon/<id>', methods=['PUT'])
@jwt_required()
def update_pokemon(id):
  
    try:
        data = request.get_json()

        pokemon = MyPokemon.query.filter_by(id=current_identity.id)[int(id)-1]

        pokemon.name = data['name']
        db.session.add(pokemon)
        db.session.commit()
        return 'Updated'
    except:
        return 'Invalid id or unauthorized'

#Release/Delete a Pokemon caught by a user
@app.route('/mypokemon/<id>', methods=['DELETE'])
@jwt_required()
def release_pokemon(id):
    try:
        pokemon = MyPokemon.query.filter_by(id=current_identity.id)[int(id)-1]

        db.session.delete(pokemon) # delete the object
        db.session.commit()
        return 'Released ' + pokemon.name, 204
    except:
        return 'Invalid id or unauthorized'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)