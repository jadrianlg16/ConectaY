from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import json_util
from sshtunnel import SSHTunnelForwarder
import pymongo
import json

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

def serialize(doc):
    return json.loads(json_util.dumps(doc))




@app.route('/get_all_collections', methods=['GET'])
def get_all_collections():
    collections_data = {
        'organizations': [serialize(org) for org in db.organizations.find()],
        'clients': [serialize(client) for client in db.clients.find()],
        'posts': [serialize(post) for post in db.posts.find()],
        'notifications': [serialize(notification) for notification in db.notifications.find()],
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
    response = [serialize(client) for client in db.clients.find()]
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
@app.route('/add_organization', methods=['POST'])
def add_organization():
    data = request.get_json()
    if data:
        result = db.organizations.insert_one(data)
        return jsonify({"message": "Organization added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.get_json()
    if data:
        result = db.clients.insert_one(data)
        return jsonify({"message": "Client added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

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
@app.route('/update_organization/<string:org_alias>', methods=['PUT'])
def update_organization(org_alias):
    data = request.get_json()
    if data:
        result = db.organizations.update_one({"alias": org_alias}, {"$set": data})
        if result.matched_count:
            return jsonify({"message": "Organization updated successfully!"}), 200
        else:
            return jsonify({"error": "Organization not found!"}), 404
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/update_person/<string:person_email>', methods=['PUT'])
def update_person(person_email):
    data = request.get_json()
    if data:
        result = db.personas.update_one({"email": person_email}, {"$set": data})
        if result.matched_count:
            return jsonify({"message": "Person updated successfully!"}), 200
        else:
            return jsonify({"error": "Person not found!"}), 404
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/update_post/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    if data:
        result = db.posts.update_one({"_id": pymongo.ObjectId(post_id)}, {"$set": data})
        if result.matched_count:
            return jsonify({"message": "Post updated successfully!"}), 200
        else:
            return jsonify({"error": "Post not found!"}), 404
    else:
        return jsonify({"error": "Invalid data!"}), 400
############################################################################################################


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        server.stop()  
