# from flask import Flask, jsonify
# from flask_pymongo import PyMongo

# app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/Testdb"
# mongo = PyMongo(app)

# @app.route('/items', methods=['GET'])
# def get_items():
#     items_cursor = mongo.db.items.find()  
#     response = []
#     for item in items_cursor:
#         item['_id'] = str(item['_id'])  
#         response.append(item)
#     return jsonify(response)

# @app.route('/org', methods=['GET'])
# def get_orgs():
#     orgs = mongo.db.org.find()
#     response_data = []
#     for org in orgs:
#         org['_id'] = str(org['_id'])  
#         response_data.append(org)
#     return jsonify(response_data)

# @app.route('/org', methods=['POST'])
# def create_org():
#     data = request.get_json()
#     if data:
#         result = mongo.db.org.insert_one(data)
#         return jsonify({"message": "Organization created successfully!", "_id": str(result.inserted_id)}), 201
#     else:
#         return jsonify({"error": "Invalid data!"}), 400

from flask import Flask, jsonify
from flask_pymongo import PyMongo
from bson import json_util
from flask import request

import json


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Prototype"
mongo = PyMongo(app)

def serialize(doc):
    return json.loads(json_util.dumps(doc))
############################################################################################################
@app.route('/get_all_collections', methods=['GET'])
def get_all_collections():
    collections_data = {
        'organizations': [serialize(org) for org in mongo.db.organizations.find()],
        'clients': [serialize(client) for client in mongo.db.clients.find()],
        'posts': [serialize(post) for post in mongo.db.posts.find()],
        'notifications': [serialize(notification) for notification in mongo.db.notifications.find()],
        'tags': [serialize(tag) for tag in mongo.db.tags.find()]
    }
    return jsonify(collections_data), 200
############################################################################################################
@app.route('/get_organizations', methods=['GET'])
def get_organizations():
    response = [serialize(org) for org in mongo.db.organizations.find()]
    return jsonify(response), 200

@app.route('/get_clients', methods=['GET'])
def get_clients():
    response = [serialize(client) for client in mongo.db.clients.find()]
    return jsonify(response), 200

@app.route('/get_posts', methods=['GET'])
def get_posts():
    response = [serialize(post) for post in mongo.db.posts.find()]
    return jsonify(response), 200

@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    response = [serialize(notification) for notification in mongo.db.notifications.find()]
    return jsonify(response), 200

@app.route('/get_tags', methods=['GET'])
def get_tags():
    response = [serialize(tag) for tag in mongo.db.tags.find()]
    return jsonify(response), 200

############################################################################################################
@app.route('/add_organization', methods=['POST'])
def add_organization():
    data = request.get_json()
    if data:
        result = mongo.db.organizations.insert_one(data)
        return jsonify({"message": "Organization added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_client', methods=['POST'])
def add_client():
    data = request.get_json()
    if data:
        result = mongo.db.clients.insert_one(data)
        return jsonify({"message": "Client added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_post', methods=['POST'])
def add_post():
    data = request.get_json()
    if data:
        result = mongo.db.posts.insert_one(data)
        return jsonify({"message": "Post added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_notification', methods=['POST'])
def add_notification():
    data = request.get_json()
    if data:
        result = mongo.db.notifications.insert_one(data)
        return jsonify({"message": "Notification added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400

@app.route('/add_tag', methods=['POST'])
def add_tag():
    data = request.get_json()
    if data:
        result = mongo.db.tags.insert_one(data)
        return jsonify({"message": "Tag added successfully!", "_id": str(result.inserted_id)}), 201
    else:
        return jsonify({"error": "Invalid data!"}), 400
############################################################################################################


if __name__ == '__main__':
    app.run(debug=True)
#    app.run(host='0.0.0.0', debug=True)


