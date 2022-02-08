import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

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
    })

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
    # get and prepare the form input
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    # Because new_recipe is a dictionary, it needs to be converted into json
    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    new_drink.insert()

    # db.session.add(new_drink)
    # db.session.flush()
    # new_drink_id = new_drink.id
    # db.session.commit()

    # new_drinkle = Drink.query.filter(Drink.id == new_drink_id).one_or_none()

    # get all drinks and order by ID
    all_drinks = Drink.query.order_by(Drink.id).all()
    
    # get the last drink in the list - assumes it's the last one
    all_drinks = [all_drinks[-1]]

    drink = []
    for drinky in all_drinks:
       drink.append(drinky.long())

    return jsonify({
        'success': True,
        'drinks': drink
    })


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
def edit_drink(self, id):
    drink = Drink.query.get(id)
    print('drink = ', drink)
    body = request.get_json()

    drink = []

    return jsonify({
        "success": True,
        "drinks": drink
    })

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
