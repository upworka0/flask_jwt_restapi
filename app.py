from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Dog %r>' % self.name


@app.route('/user', methods=['GET'])
def get_all_users():
    """
    endpoint : /user
    Get all users from users table
    :return: JSON
    """
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['email'] = user.email
        user_data['id'] = user.id
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/user/<user_id>', methods=['GET'])
def get_one_user(user_id):
    """
    Get a user by Id
    :param user_id: int
    :return: JSON
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'No user found!'})
    user_data = {}
    user_data['email'] = user.email
    user_data['id'] = user.id
    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
def create_user():
    """
    Create new user with email and password
    :return: JSON
    """
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(email=data['email'], password = hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user by Id
    :param user_id: int
    :return: JSON
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'})


# log in to get JWT token
#####################################################################################################
def authenticate(email, password):
    """
    Authenticate with email and password
    :param email: str
    :param password: str
    :return: Boolean
    """
    user = User.query.filter(User.email == email).scalar()
    if user:
        if check_password_hash(user.password, password):
            return True
    return False


@app.route('/login', methods=['POST'])
def login():
    """
    Log in and get JWT token
    :return: JSON
    """
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not authenticate(email, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    ret = {
        'access_token': create_access_token(identity=email),
        'refresh_token': create_refresh_token(identity=email)
    }
    return jsonify(ret), 200

# endpoint to get refresh token
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Get jwt token using refresh token
    :return: JSON
    """
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


####################################################################################################################
@app.route('/dog', methods=['GET'])
@jwt_required
def get_all_dogs():
    """
    Get all dogs
    :return: JSON
    """
    dogs = Dog.query.all()
    output = []
    for dog in dogs:
        dog_data = {}
        dog_data['id'] = dog.id
        dog_data['name'] = dog.name
        dog_data['age'] = dog.age
        output.append(dog_data)
    return jsonify({'dogs': output})


@app.route('/dog/<dog_id>', methods=['GET'])
@jwt_required
def get_one_dog(dog_id):
    """
    Get a dog by Id
    :param dog_id: int
    :return: JSON
    """
    dog = Dog.query.get(dog_id)

    if not dog:
        return jsonify({'message': 'No dog found!'})
    dog_data = {}
    dog_data['id'] = dog.id
    dog_data['name'] = dog.name
    dog_data['age'] = dog.age
    return jsonify({'user': dog_data})


@app.route('/dog', methods=['POST'])
@jwt_required
def create_dog():
    """
    Create new dog
    :return: JSON
    """
    data = request.get_json()
    if 'name' in data and 'age' in data:
        new_dog = Dog(name=data['name'], age=data['age'])
        db.session.add(new_dog)
        db.session.commit()
        return jsonify({'message': 'New dog created!'})
    return jsonify({'message': 'Missing fields!'})


@app.route('/dog/<dog_id>', methods=['DELETE'])
@jwt_required
def delete_dog(dog_id):
    """
    Delete a dob by id
    :param dog_id: int
    :return: JSON
    """
    dog = Dog.query.get(dog_id)

    if not dog:
        return jsonify({'message': 'No Dog found!'})

    db.session.delete(dog)
    db.session.commit()
    return jsonify({'message': 'The dog has been deleted!'})


if __name__=='__main__':
    # db.create_all()
    app.run(debug=True)
