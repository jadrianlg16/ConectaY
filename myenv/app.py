# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, redirect, flash, session
from pymongo import MongoClient, errors
from bson import json_util
from bson.objectid import ObjectId
import pymongo
import phonenumbers
import json
from werkzeug.security import generate_password_hash, check_password_hash

MONGO_DB = "ConectaMX"


# Connect directly to the MongoDB server on localhost
client = MongoClient('localhost', 27017)
db = client[MONGO_DB]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

def serialize(doc):
    return json.loads(json_util.dumps(doc))


############################################################################################################
############################################################################################################
# Routes start 

#old test route
# @app.route('/get_all_collections', methods=['GET'])
# def get_all_collections():
#     collections_data = {
#         'organizations': [serialize(org) for org in db.organizations.find()],
#         'personas': [serialize(persona) for persona in db.personas.find()],
#         'posts': [serialize(post) for post in db.posts.find()],
#         # 'notifications': [serialize(notification) for notification in db.notifications.find()],
#         'tags': [serialize(tag) for tag in db.tags.find()]
#     }
#     return jsonify(collections_data), 200

############################################################################################################
# GET requests section

@app.route('/get_organizations', methods=['GET'])
def get_organizations():
    response = [serialize(org) for org in db.organizations.find()]
    return jsonify(response), 200
@app.route('/get_organization', methods=['POST'])
def get_organization():
    data = request.get_json()
    rfc = data.get('rfc')
    password = data.get('password')
    if rfc and password:
        org = db.organizations.find_one({'RFC': rfc, 'password': password})
        if org:
            return jsonify(serialize(org)), 200
        else:
            return jsonify({'error': 'Organization not found'}), 404
    else:
        return jsonify({'error': 'Missing parameters'}), 400

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

@app.route('/get_tags', methods=['GET'])
def get_tags():
    response = [serialize(tag) for tag in db.tags.find()]
    return jsonify(response), 200

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
            
            # Removing duplicates by converting the list into a set and then back to a list
            favorites_ids = list(set(favorites_ids))
            
            # Finding organizations whose IDs are in the person's favorites array
            favorite_orgs = [serialize(org) for org in db.organizations.find({"_id": {"$in": [ObjectId(fav_id) for fav_id in favorites_ids]}})]
            
            return jsonify(favorite_orgs), 200
        else:
            return jsonify({"error": "Person not found!"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_favorite_by_phone/<string:phone>', methods=['GET'])
def check_favorite_by_phone(phone):
    try:
        # Get the organization ID from the request arguments
        org_id = request.args.get('org_id')
        
        # Ensure an organization ID is provided
        if not org_id:
            return jsonify({"error": "Organization ID not provided!"}), 400

        # Find the person by phone
        person = db.personas.find_one({"phone": phone})

        # Ensure the person is found
        if not person:
            return jsonify({"error": "Person not found!"}), 404

        # Check if the organization ID is in the person's favorites
        if org_id in person.get('favorites', []):
            return jsonify({"message": "Organization ID is in favorites!"}), 200
        else:
            return jsonify({"message": "Organization ID is not in favorites!"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


############################################################################################################
# POST requests section

@app.route('/register_client', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        client_name = request.json.get('name', "")
        email = request.json.get('email', "")
        phone_number = request.json.get('phone', "")
        password = request.json.get('password', "")
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
                    'interestedTags': []
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
        data = request.get_json()
        
        error = None
        db.organizations.create_index('RFC', unique=True)

        if not data.get('RFC') or data.get('RFC').isspace():
            error = 'Es obligatorio ingresar un RFC.'
            return error, 400
        elif not data.get('password'):
            error = 'Es obligatorio crear una contrasena.'
            return error, 400

        if error is None:
            try:
                hashed_password = generate_password_hash(data.get('password'))
                organizations = db.organizations
                
                # Nesting location, contact, and socialMedia info
                organization_data = {
                    'name': data.get('name'),
                    'alias': data.get('alias'),
                    'location': {
                        'address': data.get('address'),
                        'city': data.get('city'),
                        'state': data.get('state'),
                        'country': data.get('country'),
                        'zip': data.get('zip'),
                    },
                    'contact': {
                        'email': data.get('email'),
                        'first_phone': data.get('first_phone'),
                        'second_phone': data.get('second_phone'),
                    },
                    'serviceHours': data.get('serviceHours'),
                    'website': data.get('website'),
                    'socialMedia': {
                        'facebook': data.get('facebook'),
                        'twitter': data.get('twitter'),
                        'instagram': data.get('instagram'),
                        'linkedIn': data.get('linkedIn'),
                        'youtube': data.get('youtube'),
                        'tiktok': data.get('tiktok'),
                        'whatsapp': data.get('whatsapp'),
                    },
                    'missionStatement': data.get('missionStatement'),
                    'logo': '',  # Assuming logo will be added later
                    'tags': [],  # Assuming tags will be added later
                    'postId': [],  # Assuming postId will be added later
                    'followers': [],  # Assuming followers will be added later
                    'password': hashed_password,
                    'RFC': data.get('RFC'),
                }

                id = organizations.insert_one(organization_data)
                response = {
                    'message': 'Se registro exitosamente el usuario.',
                    'id': str(id.inserted_id),
                    # Add any other fields you want to return in the response
                }
                return jsonify(response), 201
            except errors.DuplicateKeyError:
                return f"El numero de RFC {data.get('RFC')} ya esta registrado.", 400
        return error, 400

@app.route('/login_client', methods=['GET', 'POST'])
def login_client():
    if request.method == 'POST':
        phone_number = request.json['phone']
        password = request.json['password']
        error = None

        try:
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
            return jsonify({'client_info': client_info_dict}), 200

        flash(error)

    return redirect('/login_client')

@app.route('/login_organization', methods=['POST'])
def login_organization():
    if request.method == 'POST':
        rfc_code = request.json['RFC']
        password = request.json['password']
        error = None
        organization_rfc = db.organizations.find_one({'RFC': rfc_code})

        if organization_rfc is None:
            error = 'Numero de RFC incorrecto.'
            return error, 400
        elif not check_password_hash(organization_rfc['password'], password):
            error = 'Contrasena incorrecta.'
            return error, 400

        if error is None:
            session.clear()
            session['RFC'] = str(organization_rfc['_id'])
            organization_info_json= json_util.dumps(organization_rfc)
            organization_info_dict = json_util.loads(organization_info_json)
            organization_info_dict.pop('_id', None)
            return jsonify({'organization_info': organization_info_dict}), 200

        flash(error)

    return redirect('/login_organization')

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

@app.route('/add_favorite_by_phone/<string:phone>', methods=['POST'])
def add_favorite_by_phone(phone):
    try:
        # Get the organization ID from the request data
        org_id = request.json.get('org_id')
        
        # Ensure an organization ID is provided
        if not org_id:
            return jsonify({"error": "Organization ID not provided!"}), 400

        # Find the person by phone
        person = db.personas.find_one({"phone": phone})

        # Ensure the person is found
        if not person:
            return jsonify({"error": "Person not found!"}), 404

        # Add the organization ID to the person's favorites only if it's not already there
        result = db.personas.update_one({"phone": phone}, {"$addToSet": {"favorites": org_id}})
        
        if result.modified_count > 0:
            return jsonify({"message": "Favorite added successfully!"}), 200
        else:
            return jsonify({"message": "Organization ID already in favorites!"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/remove_favorite_by_phone/<string:phone>', methods=['POST'])
def remove_favorite_by_phone(phone):
    try:
        # Get the organization ID from the request data
        org_id = request.json.get('org_id')
        
        # Ensure an organization ID is provided
        if not org_id:
            return jsonify({"error": "Organization ID not provided!"}), 400

        # Find the person by phone
        person = db.personas.find_one({"phone": phone})

        # Ensure the person is found
        if not person:
            return jsonify({"error": "Person not found!"}), 404

        # Remove the organization ID from the person's favorites
        db.personas.update_one({"phone": phone}, {"$pull": {"favorites": org_id}})
        
        return jsonify({"message": "Favorite removed successfully!"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



############################################################################################################
# PUT requests section

@app.route('/update_organization/<string:rfc>', methods=['PUT'])
def update_organization(rfc):
    data = request.get_json()
    if data:
        try:
            # Updating the organization using RFC
            result = db.organizations.update_one({"RFC": rfc}, {"$set": data})
            
            if result.matched_count:
                return jsonify({"message": "Organization updated successfully!"}), 200
            else:
                return jsonify({"error": "Organization not found!"}), 404
                
        except Exception as e:
            # Handling any exception that may occur
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






############################################################################################################
# Run python:

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        server.stop()  
