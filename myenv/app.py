from flask import Flask, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Testdb"
mongo = PyMongo(app)

@app.route('/items', methods=['GET'])
def get_items():
    items_cursor = mongo.db.items.find()  
    response = []
    for item in items_cursor:
        item['_id'] = str(item['_id'])  
        response.append(item)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

