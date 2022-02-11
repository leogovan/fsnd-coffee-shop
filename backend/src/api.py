import os
from queue import Empty
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
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
def retrieve_drinks():
    all_drinks = Drink.query.all()
    # returns a list of DB objects (not dictionaries)
    print("all_drinks = ", all_drinks[0])
    print("all_drinks type = ", type(all_drinks[0]))
    
    drinks = []
    for drink in all_drinks:
       drinks.append(drink.short())
    
    
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks
    })


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
def get_drinks_detail(self):
    all_drinks = Drink.query.all()
    drinks = []
    for drink in all_drinks:
        drinks.append(drink.long())
    
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

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
def new_drink(self):
    try:
        # get and prepare the form input
        body = request.get_json()
        # Check for value in body
        if body is None:
            abort(404)
        else:
            new_title = body.get('title', None)
            new_recipe = body.get('recipe', None)
    except:
        abort(422)

    # Because new_recipe is a dictionary, it needs to be converted into json
    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    try:
        # Get the ID of the new drink record before it is commited and store
        db.session.add(new_drink)
        db.session.flush()
        new_drink_id = new_drink.id
    
        # Commit to DB
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(500)

    try:
        # Get the new drink object from the db by ID
        # Apply class method long() to format it
        drink = Drink.query.filter(Drink.id == new_drink_id).one_or_none().long()

        return jsonify({
            'success': True,
            'drinks': drink
        }), 200

    except:
        abort(500)
    """
    # Alternative approach:

    get all drinks and order by ID
    all_drinks = Drink.query.order_by(Drink.id).all()
    
    get the last drink in the list - assumes it's the last one to  be created
    all_drinks = [all_drinks[-1]]

    drink = []
    for drinky in all_drinks:
        drink.append(drinky.long())
    """


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
# def edit_drink(self, id):
#     body = request.get_json()
#     title_update = body.get('title', None)
#     recipe_update = body.get('recipe', None)

#     drink = Drink.query.get(id)
#     drink.title = title_update
#     drink.recipe = json.dumps(recipe_update)
#     drink.update()

#     return jsonify({
#         "success": True,
#         "drinks": drink.long()
#     }), 200

def edit_drink(self, id):
    try: 
        body = request.get_json()
        print("I am body: ", body)
        if body is None:
            abort(404)
        else:
            title_update = body.get('title')
            recipe_update = body.get('recipe')
    except:
        abort(422)

    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        # print('drink = ', drink)
        else:
            drink.title = title_update
            drink.recipe = json.dumps(recipe_update)
            drink.update()

            return jsonify({
                "success": True,
                "drinks": drink.long()
            }), 200
    
    except:
        abort(500)

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
def delete_drink(self, id):
    try:
        drink = Drink.query.get(id)

        if drink is None:
            abort(422)
        else:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': id
            }), 200
    
    except:
        abort(500)


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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
