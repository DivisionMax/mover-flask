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
                if check_password(result[3],_password):
                    output = jsonify({
                        "auth":"success",
                        "message":"login successful",
                        "username": result[2],
                        "id": result[0]
                        })
                else:
                    output= jsonify({
                        "auth":"fail",
                        "message":"login unsuccessful"
                        })
            else:
                output = jsonify({
                    "auth":"fail",
                    "message":"login unsuccessful"
                    })
        else:
            output = jsonify({
                "auth":"fail",
                "message":"parameters cannot be empty"
                })
        return output

        cursor.close()
    except KeyError:
        app.logger.warn('The data was malformed')
        return jsonify({
            "auth":"fail",
            "message":"parameters cannot be empty"})

@app.route('/register', methods=['POST']) #data is submitted
def register():
    try:
        #POST - request.args - URL parameters
        _email = request.form['email'] 
        username = _email.rsplit('@', 1)[0]
        _password = request.form['password']
        _passwordConfirm = request.form['password_confirm']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mobile_app_users WHERE emailAddress = %s", (_email,))
        result = cursor.fetchone()

        if result is None:
            if _password == _passwordConfirm:
                # need to check they don't exist beforehand.
                # stored passwords must be hashed
                password_hash = hash_password(_password)
                cursor.execute("INSERT INTO mobile_app_users (emailAddress,password,username) values (%s,%s,%s)", (_email, password_hash, username))
                conn.commit()
                id = cursor.lastrowid
                if id:
                    return jsonify({
                        "auth":"success",
                        "message":"registration confirmed",
                        "username": username, 
                        "id": id
                        })
            else:
                return jsonify({"auth":"fail", "message" : "passwords do not match"})
        else:
                return jsonify({"auth":"fail", "message" : "please use another email"})

    except KeyError:
        app.logger.warn('invalid inputs')
        return jsonify({
            "auth":"fail",
            "message":"invalid inputs"})

@app.route('/accidents', methods=['GET']) #data is submitted
def getAccidents():
    try:

        _userId = request.args.get('userId')
        _type = request.args.get('type')
        
        if _userId and _type:

            if _type == 'runner' or _type == 'car':

                cursor = conn.cursor()
                # parametized - prevent SQL injection
                cursor.execute("SELECT accidentId as id, accidentTime as time,X(location) as x, Y(location) as y  FROM simplerunningaccidents WHERE mobileAppUserId = %s", (_userId,))
                
                results = cursor.fetchall()

                if results:
                    data = []
                    app.logger.info(results)
                    # jsonify returns a response
                    for row in results:
                        app.logger.info(row)
                        #data will be a list of lists
                        data.append(
                            {"id": row[0],
                            "datetime": row[1],
                            "latitude": row[2],
                            "longitude": row[3]
                        }) # or simply data.append(list(row))
                        app.logger.info(data)

                    output = jsonify({
                        "results":data
                        })
                else:
                    output= jsonify({
                            "results":[]                            
                            })
                cursor.close()
            else:
                return jsonify({
                    "result":"fail",
                    "message":"no accident added"})

            
        else:
            output = jsonify({
                "auth":"fail",
                "message":"parameters cannot be empty"
                })

        return output
        

    except KeyError:
        return jsonify({
            "result":"fail",
            "message":"invalid inputs"
            })

@app.route('/accident', methods=['POST']) #data is submitted
def accident():
    try:
        #POST - request.args - URL parameters
        _type = request.form['type']
        _longitude = request.form['longitude']
        _latitude = request.form['latitude']
        _timeOfAccidentTimestamp = request.form['time-of-accident']
        _userId = request.form['userId']

        app.logger.info('Time of Accident: %s', (_timeOfAccidentTimestamp,))
        
        if _type and _longitude and _latitude and _timeOfAccidentTimestamp and _userId:
            # there should actually be a different statement for car 
            if _type == 'runner' or _type == 'car':
                # runner accident
                cursor = conn.cursor()
                # cursor.execute("SELECT userID FROM web_app_users WHERE emailAddress = %s", (_email,))
                # _userID = result = cursor.fetchone()
                # unix timestamp is more robust than handling specific string formats
                cursor.execute("INSERT INTO simplerunningaccidents (accidentTime,location,mobileAppUserId) values (from_unixtime(%s),point(%s,%s),%s)", (_timeOfAccidentTimestamp, _longitude,_latitude, _userId))
                conn.commit()
                return jsonify({
                    "result":"success",
                    "message":"accident added"})

            else:
                return jsonify({
                    "result":"fail",
                    "message":"no accident added"})
        else:
            return jsonify({
                "result":"fail",
                "message":"invalid inputs"
                })
    except KeyError:
        return jsonify({
            "result":"fail",
            "message":"invalid inputs"
            })

if __name__ == "__main__":
    #app.run() #local
    # http://10.0.0.6:5000
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True) #reloads
