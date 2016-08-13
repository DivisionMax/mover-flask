"""
Basic server functionality for Mover. Includes basic bootstrap.
"""
import sys, traceback
from flask import Flask, render_template, request
from flask import jsonify
from password_service import hash_password, check_password
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


@app.route('/')
def main():
    app.logger.debug('Requested')
    return render_template('index.html')

@app.route('/login', methods=['POST']) #data is submitted
def login():
    try:
        _email = request.form['email'] #POST - request.args - URL parameters
        _password = request.form['password']
        # validate the received values
        if _email and _password:

            # only hashed passwords are stored
            passwordHash = hash_password(_password)
            cursor = conn.cursor()
            # parametized - prevent SQL injection
            cursor.execute("SELECT * FROM web_app_users WHERE emailAddress = %s and password = %s", (_email,passwordHash))
            result = cursor.fetchone()
            if result is not None:
                # jsonify returns a response
                result = jsonify({'id': result[0]})
                print (result)
                return result, 200
            else:
                return 'Unsuccessful login, check inputs', 200
        else:
            return 'Email and password must be submitted', 500
        cursor.close()
    except KeyError:
        print ("The data was malformed")
        app.logger.warn('The data was malformed')
        return 'Email and password must be submitted', 500

# doesn't interact with the database yet.
@app.route('/register', methods=['POST']) #data is submitted
def register():
    try:
        _email = request.form['email'] #POST - request.args - URL parameters
        _password = request.form['password']
        _passwordConfirm = request.form['password_confirm']
        
        if _password == _passwordConfirm:
            cursor = conn.cursor()
            # stored passwords must be hashed
            password_hash = hash_password(_password)
            cursor.execute("INSERT INTO web_app_users (emailAddress,password,password_hash) values (%s,%s)", (_email,password_hash))
            db.commit()
            return jsonify({"success":"registration confirmed"})
        else:
            return jsonify({"error":"passwords do not match"})
    except KeyError:
        app.logger.warn('invalid inputs')
        return jsonify({"error":"invalid inputs"})


@app.route('/post-accident', methods=['POST']) #data is submitted
def postAccident():
    try:
        _userId = request.form['userId'] #POST - request.args - URL parameters
        _longitude = request.form['longitude']
        _latitude = request.form['latitude']

        # server doesn't create the time because incident may not have occured at this time
        _time = request.form['time']

        # validate the received values
        if _userId and _longitude and _latitude and _time:
        
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ACCIDENTS() VALUES(%s, %s, %s, %s)", (_userId, _longitude, _latitude, _time)) #last value is a timestamp          
            conn.commit()
            if cursor.lastrowid:
                response = "Accident received and inserted"
                app.logger.info(response)
                return jsonify({"msg":response},200)
            else:
                response = "Accident could not be inserted"
                app.logger.warn(response)
                return jsonify({"msg":response},500)
            return jsonify({"msg":"well done"},500)

        else:
            return 'Invalid accident information', 500

        # cursor.close()
    except KeyError:
        app.logger.warn('Invalid accident information')
        response = "Accident could not be inserted"
        app.logger.warn(response)
        return jsonify({"msg":response},500)


if __name__ == "__main__":
    #app.run() #local
    # http://10.0.0.6:5000
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True) #reloads
