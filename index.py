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
                                   database='mover',
                                   user='mover',
                                   password='flower mine smile tonight')
    if conn.is_connected():
        print('Connected to MySQL database')

except Error as e:
    print(e)

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
            # parametize, security
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE user_email = %s", (_email,))
            # cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (_email, _password))
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
        _password = request.form['pass']
        if _email and _password:
            return 'Registration details receieved', 200
        else:
            return 'Email and password must be submitted', 500
    except KeyError:
        print ("The data was malformed")
        app.logger.warn('The data was malformed')
        return 'The data was malformed', 500


@app.route('/post-accident', methods=['POST']) #data is submitted
def postAccident():
    try:
        _userId = request.form['userId'] #POST - request.args - URL parameters
        _longitude = request.form['longitude']
        _latitude = request.form['latitude']
        _time = request.form['time']

        # validate the received values
        if _userId and _longitude and _latitude and _time:
        
            # parametize, security
            # cursor = conn.cursor()
            # # cursor.execute("INSERT INTO ACCIDENTS() VALUES(%s, %s, %s, %s)", (_userId, _longitude, _latitude, _time)) #last value is a timestamp
            
            # conn.commit()

            # if cursor.lastrowid:
            #     response = "Accident received and inserted"
            #     app.logger.info(response)
            #     return jsonify({"msg":response},200)
            # else:
            #     response = "Accident could not be inserted"
            #     app.logger.warn(response)
            #     return jsonify({"msg":response},500)
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
    app.run(debug=True) #reloads
