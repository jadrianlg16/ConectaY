# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, redirect, flash, session
from pymongo import MongoClient, errors
from bson import json_util
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder
import pymongo
import phonenumbers
import json
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

MONGO_HOST = "10.14.255.172"  
MONGO_DB = "ConectaMX"
MONGO_USER = "admin01"
MONGO_PASS = "Tec$2023"

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', 27017)
)

server.start()

client = MongoClient('127.0.0.1', server.local_bind_port)  
db = client[MONGO_DB]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

def serialize(doc):
    return json.loads(json_util.dumps(doc))




@app.route('/get_all_collections', methods=['GET'])
def get_all_collections():
    collections_data = {
        'organizations': [serialize(org) for org in db.organizations.find()],
        'personas': [serialize(persona) for persona in db.personas.find()],
        'posts': [serialize(post) for post in db.posts.find()],
        # 'notifications': [serialize(notification) for notification in db.notifications.find()],
        'tags': [serialize(tag) for tag in db.tags.find()]
    }
    return jsonify(collections_data), 200

############################################################################################################
# GET requests section
@app.route('/get_organizations', methods=['GET'])
def get_organizations():
    response = [serialize(org) for org in db.organizations.find()]
    return jsonify(response), 200

@app.route('/get_clients', methods=['GET'])
def get_clients():
    response = [serialize(persona) for persona in db.personas.find()]
    return jsonify(response), 200

@app.route('/get_posts', methods=['GET'])
def get_posts():
    response = [serialize(post) for post in db.posts.find()]
    return jsonify(response), 200


@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    response = [serialize(notification) for notification in db.notifications.find()]
    return jsonify(response), 200

# @app.route('/get_tags', methods=['GET'])
# def get_tags():
#     response = [serialize(tag) for tag in db.tags.find()]
#     return jsonify(response), 200

@app.route('/get_tags', methods=['GET'])
def get_tags():
    response = [serialize(tag) for tag in db.tags.find()]
    return jsonify(response), 200


############################################################################################################
# POST requests section

'''
@app.route('/add_organization', methods=['POST'])
def add_organization():
    data = request.get_json()
    if data:
        result = db.organizations.insert_one(data)
        return jsonify({"message": "Organization added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400
'''

@app.route('/register_client', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        client_name = request.json['name']
        email = request.json['email']
        phone_number = request.json['phone']
        password = request.json['password']
        error = None
        db.personas.create_index('phone', unique=True)

        if not phone_number or phone_number.isspace():
            error = 'Es oblligatorio ingresar un numero de telefono.'
            return error, 400
        elif not password:
            error = 'Es obligatorio crear una contrasena.'
            return error, 400

        try:
            # Si el prefijo internacional es None, el usuario debe escribirlo (ej. +52)
            # Si se define una region en None (ej. 'MX') el usuario solo debe escribir los 10 digitos de su num. de tel.
            phone_number_info = phonenumbers.parse(phone_number, 'MX')  
            phone_number_formatted = phonenumbers.format_number(phone_number_info, phonenumbers.PhoneNumberFormat.E164)
            phone_number_test = phonenumbers.is_valid_number(phone_number_info)
        except phonenumbers.NumberParseException:
            error = 'El numero de telefono ingresado no es valido.'
            return error, 400
        
        if phone_number_test is False:
            error = 'El numero de telefono ingresado no es valido.'
            return error, 400
        
        if error is None:
            try:
                hashed_password = generate_password_hash(password)
                users = db.personas
                id = users.insert_one({
                    'name': client_name,
                    'email': email,
                    'phone': phone_number_formatted,
                    'password': hashed_password,
                    'favorites': [],
                    'intrestedTags': []
                })
                response = {
                    'message': 'Se registro exitosamente el usuario.',
                    'id': str(id.inserted_id),
                    'name': client_name,
                    'email': email,
                    'phone': phone_number_formatted,
                    'password': hashed_password
                }
                return response, 201
            except errors.DuplicateKeyError:
                return f"El numero de telefono {phone_number_formatted} ya esta registrado.", 400
            else:
                return redirect('/login_client')
        flash(error)

@app.route('/register_organization', methods=['GET', 'POST'])
def register_organization():
    if request.method == 'POST':
        organization_name = request.json['name']
        email = request.json['email']
        phone_number = request.json['phone']
        password = request.json['password']
        rfc_code = request.json['RFC']

        error = None
        db.organizations.create_index('RFC', unique=True)

        if not rfc_code or rfc_code.isspace():
            error = 'Es oblligatorio ingresar un RFC.'
            return error, 400
        elif not password:
            error = 'Es obligatorio crear una contrasena.'
            return error, 400

        if error is None:
            try:
                hashed_password = generate_password_hash(password)
                users = db.personas
                id = users.insert_one({
                    'name': organization_name,
                    'email': email,
                    'phone': phone_number,
                    'password': hashed_password,
                    'RFC': rfc_code
                })
                response = {
                    'message': 'Se registro exitosamente el usuario.',
                    'id': str(id.inserted_id),
                    'name': organization_name,
                    'email': email,
                    'phone': phone_number,
                    'password': hashed_password,
                    'RFC': rfc_code
                }
                return response, 201
            except errors.DuplicateKeyError:
                return f"El numero de RFC {rfc_code} ya esta registrado.", 400
            else:
                return redirect('/login_organization')
        flash(error)

@app.route('/login_client', methods=['GET', 'POST'])
def login_client():
    if request.method == 'POST':
        phone_number = request.json['phone']
        password = request.json['password']
        error = None

        try:
            # Parse and format phone number
            phone_number_info = phonenumbers.parse(phone_number, 'MX')
            phone_number_formatted = phonenumbers.format_number(phone_number_info, phonenumbers.PhoneNumberFormat.E164)
            phone_number_test = phonenumbers.is_valid_number(phone_number_info)
        except phonenumbers.NumberParseException:
            error = 'El numero de telefono ingresado no es valido.'
            return error, 400
        
        if  not phone_number_test:
            error = 'El numero de telefono ingresado no es valido.'
            return error, 400

        client_phone = db.personas.find_one({'phone': phone_number_formatted})

        if client_phone is None:
            error = 'Numero de telefono incorrecto.'
            return error, 400
        elif not check_password_hash(client_phone['password'], password):
            error = 'Contrasena incorrecta.'
            return error, 400

        if error is None:
            session.clear()
            session['phone_id'] = str(client_phone['_id'])
            # Serialize MongoDB document to JSON string
            client_info_json= json_util.dumps(client_phone)
            # Parse JSON stirng to dictionary
            client_info_dict = json_util.loads(client_info_json)
            # Remove MongoDB _id field (which is not JSON-serializable)
            client_info_dict.pop('_id', None)
            # Include user info
            return jsonify({'client_info': client_info_dict})

        flash(error)

    return redirect('/login_client')


'''
@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.get_json()
    if data:
        result = db.personas.insert_one(data)
        return jsonify({"message": "Client added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400
'''

@app.route('/add_post', methods=['POST'])
def add_post():
    data = request.get_json()
    if data:
        result = db.posts.insert_one(data)
        return jsonify({"message": "Post added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_notification', methods=['POST'])
def add_notification():
    data = request.get_json()
    if data:
        result = db.notifications.insert_one(data)
        return jsonify({"message": "Notification added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_tag', methods=['POST'])
def add_tag():
    data = request.get_json()
    if data:
        result = db.tags.insert_one(data)
        return jsonify({"message": "Tag added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400
############################################################################################################
# UPDATE requests section

# @app.route('/update_organization/<string:org_alias>', methods=['PUT'])
# def update_organization(org_alias):
#     data = request.get_json()
#     if data:
#         result = db.organizations.update_one({"alias": org_alias}, {"$set": data})
#         if result.matched_count:
#             return jsonify({"message": "Organization updated successfully!"}), 200
#         else:
#             return jsonify({"error": "Organization not found!"}), 404
#     else:
#         return jsonify({"error": "Invalid data!"}), 400

# @app.route('/update_person/<string:person_email>', methods=['PUT'])
# def update_person(person_email):
#     data = request.get_json()
#     if data:
#         result = db.personas.update_one({"email": person_email}, {"$set": data})
#         if result.matched_count:
#             return jsonify({"message": "Person updated successfully!"}), 200
#         else:
#             return jsonify({"error": "Person not found!"}), 404
#     else:
#         return jsonify({"error": "Invalid data!"}), 400

# @app.route('/update_post/<string:post_id>', methods=['PUT'])
# def update_post(post_id):
#     data = request.get_json()
#     if data:
#         result = db.posts.update_one({"_id": pymongo.ObjectId(post_id)}, {"$set": data})
#         if result.matched_count:
#             return jsonify({"message": "Post updated successfully!"}), 200
#         else:
#             return jsonify({"error": "Post not found!"}), 404
#     else:
#         return jsonify({"error": "Invalid data!"}), 400

############################################################################################################
#SPECIFIC GETS



'''
@app.route('/get_organization/<string:org_oid>', methods=['GET'])
def get_organization(org_oid):
    try:
        org = db.organizations.find_one({"_id": ObjectId(org_oid)})
        if org:
            return jsonify(serialize(org)), 200
        else:
            return jsonify({"error": "Organization not found!"}), 404
    except:
        return jsonify({"error": "Invalid ObjectId format!"}), 400
'''



@app.route('/get_client/<string:client_phone>', methods=['GET'])
def get_client(client_phone):
    client = db.personas.find_one({"phone": client_phone})
    if client:
        return jsonify(serialize(client)), 200
    else:
        return jsonify({"error": "Client not found!"}), 404

@app.route('/get_org_post/<string:org_id>', methods=['GET'])
def get_org_posts(org_id):
    posts = list(db.posts.find({"organizationId": org_id}))
    if posts:
        return jsonify([serialize(post) for post in posts]), 200
    else:
        return jsonify({"error": "Posts not found!"}), 404





#############################################################################################################

## no borres este comentario
# @app.route('/update_organization/<string:org_alias>', methods=['PUT'])
# def update_organization(org_alias):
#     data = request.get_json()
#     if data:
#         result = db.organizations.update_one({"name": org_alias}, {"$set": data})
#         if result.matched_count:
#             return jsonify({"message": "Organization updated successfully!"}), 200
#         else:
#             return jsonify({"error": "Organization not found!"}), 404
#     else:
#         return jsonify({"error": "Invalid data!"}), 400



@app.route('/update_organization/<string:org_id>', methods=['PUT'])
def update_organization(org_id):
    data = request.get_json()
    if data:
        try:
            # Converting string ID to ObjectId and updating the organization
            result = db.organizations.update_one({"_id": ObjectId(org_id)}, {"$set": data})
            
            if result.matched_count:
                return jsonify({"message": "Organization updated successfully!"}), 200
            else:
                return jsonify({"error": "Organization not found!"}), 404
                
        except Exception as e:
            # Handling invalid ObjectId error or any other exception
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "Invalid data!"}), 400



@app.route('/update_client/<string:client_phone>', methods=['PUT'])
def update_client(client_phone):
    data = request.get_json()
    if data:
        result = db.personas.update_one({"phone": client_phone}, {"$set": data})
        if result.matched_count:
            return jsonify({"message": "Client updated successfully!"}), 200
        else:
            return jsonify({"error": "Client not found!"}), 404
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/update_post/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    if data:
        result = db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": data})
        if result.matched_count:
            return jsonify({"message": "Post updated successfully!"}), 200
        else:
            return jsonify({"error": "Post not found!"}), 404
    else:
        return jsonify({"error": "Invalid data!"}), 400


#################################################################################################
# for getting orgs by tags

@app.route('/get_organizations_by_tags', methods=['GET'])
def get_organizations_by_tags():
    # Get tags from query parameters
    tags = request.args.getlist('tags')
    
    # If no tags are provided, return an error response
    if not tags:
        return jsonify({"error": "No tags provided!"}), 400

    # Query the database for organizations with any of the provided tags
    matching_organizations = db.organizations.find({"tags": {"$in": tags}})
    
    # Serialize the results and return them as a JSON response
    response = [serialize(org) for org in matching_organizations]
    return jsonify(response), 200

@app.route('/get_favorites_by_phone/<string:phone>', methods=['GET'])
def get_favorites_by_phone(phone):
    try:
        # Finding the person by phone
        person = db.personas.find_one({"phone": phone})
        
        if person:
            # Getting the favorites array from the person's document
            favorites_ids = person.get('favorites', [])
            
            # Finding organizations whose IDs are in the person's favorites array
            favorite_orgs = [serialize(org) for org in db.organizations.find({"_id": {"$in": [ObjectId(fav_id) for fav_id in favorites_ids]}})]
            
            return jsonify(favorite_orgs), 200
        else:
            return jsonify({"error": "Person not found!"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        server.stop()  
