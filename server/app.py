#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    result = [
        {"id": r.id,"name": r.name, "address": r.address
    } 
      for r in restaurants]
  
    return jsonify(result), 200

@app.route("/restaurants/<int:id>", methods=['GET'])
def get_restaurants_by_id(id):

    restaurant = Restaurant.query.get(id)
    if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        
    return jsonify ({
        "address":restaurant.address,
        "id":restaurant.id,
        "name":restaurant.name,
        "restaurant_pizzas":[{
            "id": rp.id,
            "pizza":{
                "id":rp.pizza.id,
                "ingredients":rp.pizza.ingredients,
                "name":rp.pizza.name
            },
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id
        } for rp in restaurant.restaurant_pizzas]
    }),200


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
     restaurant = Restaurant.query.get(id)
     if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
     db.session.delete(restaurant)
     db.session.commit()
     return '', 204


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas= Pizza.query.all()
    result = [
        {"id": p.id,"ingredients": p.ingredients, "name": p.name
    } 
      for p in pizzas]
  
    return jsonify(result), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
        data = request.get_json()

        if not data.get('price') or not data.get('pizza_id') or not data.get('restaurant_id'):
          return jsonify({"errors": ["validation errors"]}), 400

        try:
             restaurant_pizza = RestaurantPizza (
                price=data['price'],
                pizza_id=data['pizza_id'],     
                restaurant_id=data['restaurant_id']
             )
             db.session.add(restaurant_pizza)
             db.session.commit()
             return jsonify({
                "id": restaurant_pizza.id,
                "pizza": {
                      "id": restaurant_pizza.pizza.id,
                      "ingredients": restaurant_pizza.pizza.ingredients,
                      "name": restaurant_pizza.pizza.name
                      },
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant": {
                    "address": restaurant_pizza.restaurant.address,
                    "id": restaurant_pizza.restaurant.id,
                    "name": restaurant_pizza.restaurant.name
                  },
               "restaurant_id": restaurant_pizza.restaurant_id
               }), 201
        except Exception as e:
             db.session.rollback()
             return jsonify({"errors": ["validation errors"]}), 400  

             
if __name__ == "__main__":
    app.run(port=5555, debug=True)
