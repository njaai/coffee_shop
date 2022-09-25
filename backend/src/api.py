import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES
'''


@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(jwt):

    print(jwt)
    
    try:
        list = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in list]
    
       
        return jsonify({
            "Success": True,
            "drinks": drinks
        })
    except:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinksdetail(jwt):
    print(jwt)
    detail = Drink.query.all()
    try:
        drinks = [drink.long() for drink in detail]
    
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    print(jwt)
    body = request.get_json()

    try: 

        new_title = body.get('title', None)
        new_recipe = json.dumps(body.get('recipe', None))
        
        drink = Drink(title = new_title, recipe = new_recipe)
        
        drink.insert()
        formatted_drinks = [drink.long()]
    

        return jsonify({
            "success": True,
            "drinks": formatted_drinks
          
        })
    except:
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    print(jwt)

    body = request.get_json()

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        if 'title' in body:
            drink.title = body.get('title', 'title')
        if 'recipe' in body:
            drink.recipe = json.dumps(body.get('recipe', 'recipe'))

            drink.update()
            formatted_drinks = [drink.long()]


        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    print(jwt)

    try:
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink is None:
            abort(404, description="Resource not found")
        
        drink.delete()
        selection = Drink.query.all()
        drinks = [drink.long() for drink in selection]
            

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
       "success": False, 
       "error": 404,
       "message": " resource not found"
   }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

if __name__ == "__main__":
    app.debug = True
    app.run()
