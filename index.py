"""
Basic server functionality for Mover. Includes basic bootstrap.
"""
import sys, traceback
from flask import Flask, render_template, request
from flask import jsonify
from password_service import hash_password, check_password
from datetime import datetime
# MySQL connectivity
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# DATABASE CONFIGURATION
""" Connect to MySQL database """
conn = None

try:
    conn = mysql.connector.connect(host='localhost',
                                   database='moverdb',
                                   user='mover_user',
                                   password='resu_revom')
    if conn.is_connected():
        print('Connected to MySQL database')

except Error as e:
    print(e)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error":"page doesn't exist"}, 404)

@app.errorhandler(500)
def page_not_found(e):
    return jsonify({"error":"i broke"}, 500)

@app.route('/login', methods=['POST']) #data is submitted
def login():
    try:
        _email = request.form['email'] #POST - request.args - URL parameters
        _password = request.form['password']
        # validate the received values
        if _email and _password:

            cursor = conn.cursor()
            # parametized - prevent SQL injection
            cursor.execute("SELECT * FROM mobile_app_users WHERE emailAddress = %s", (_email,))
            
            result = cursor.fetchone()

            app.logger.info(result)
            
            if result:
                # jsonify returns a response
                if check_password(result[2],_password):
                    response = jsonify({"success":"login successful","username": result[3],"id": result[0]})
                else:
                    response = jsonify({"error":"login unsuccessful"})
            else:
                response = jsonify({"error":"login unsuccessful"})


        else:
            response = jsonify({"error":"parameters cannot be empty"})
            
        return response

        cursor.close()
    except KeyError:
        app.logger.warn('The data was malformed')
        return jsonify({"error":"parameters cannot be empty"})

@app.route('/register', methods=['POST']) #data is submitted
def register():
    try:
        #POST - request.args - URL parameters
        _email = request.form['email'] 
        username = _email.rsplit('@', 1)[0]
        _password = request.form['password']
        _passwordConfirm = request.form['password_confirm']
        
        if _password == _passwordConfirm:
            cursor = conn.cursor()
            # stored passwords must be hashed
            password_hash = hash_password(_password)
            cursor.execute("INSERT INTO mobile_app_users (emailAddress,password,username) values (%s,%s,%s)", (_email, password_hash, username))
            conn.commit()
            id = cursor.lastrowid
            if id:
                return jsonify({"success":"registration confirmed","username": username, "id": id})
        else:
            return jsonify({"error":"passwords do not match"})
    except KeyError:
        app.logger.warn('invalid inputs')
        return jsonify({"error":"invalid inputs"})


@app.route('/car-accident', methods=['POST']) #data is submitted
def caraccident():
    try:        
        _email = request.form['email'] 
        _lat = request.form['lat']
        _long = request.form['lng']
        _acc = request.form['acc']
        
        _time = datetime.datetime.utcnow()

        cursor = conn.cursor()

        cursor.execute("SELECT userID FROM web_app_users WHERE emailAddress = %s", (_email,))
            
        _userID = result = cursor.fetchone()
        
        app.logger.info(result)
        
        cursor.execute("INSERT INTO car_accidents (accidentTime,latitude,longitude,acceleration,mobile_app_users_userID) values (%s,%s,%s,%s,%s)", (_time, _lat, _long, _acc, _email,_userID))
        conn.commit()
        return jsonify({"success":"accident posted"})
    except KeyError:
        app.logger.warn('accident post failed')
        return jsonify({"error":"accident post failed"})


@app.route('/accident', methods=['POST']) #data is submitted
def accident():
    try:
        #POST - request.args - URL parameters
        _type = request.form['type']
        _longitude = request.form['longitude']
        _latitude = request.form['latitude']
        _timeOfAccident = request.form['time-of-accident']
        _userId = request.form['userId']
        app.logger.info('Time of Accident: %s', (_timeOfAccident,))
        
        if _type and _longitude and _latitude and _timeOfAccident and _userId:
            # date_object = datetime.strptime(_timeOfAccident, '%b %d %Y %I:%M%p')

            if _type == 'runner':
                # runner accident
                cursor = conn.cursor()
                # stored passwords must be hashed
                cursor.execute("INSERT INTO simplerunningaccidents (accidentTime,location,mobileAppUserId) values (%s,point(%s,%s),%s)", (_timeOfAccident, _longitude,_latitude, _userId))
                conn.commit()
                return jsonify({"success":"accident added"})
            else:
                return jsonify({"error":"no accident added"})
        else:
            return jsonify({"error":"invalid inputs"})
    except KeyError:
        app.logger.warn('invalid inputs')
        return jsonify({"error":"invalid inputs"})

if __name__ == "__main__":
    #app.run() #local
    # http://10.0.0.6:5000
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True) #reloads
