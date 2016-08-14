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

@app.route('/login', methods=['POST']) #data is submitted
def login():
    try:
        _email = request.form['email'] #POST - request.args - URL parameters
        _password = request.form['password']
        # validate the received values
        if _email and _password:

            cursor = conn.cursor()
            # parametized - prevent SQL injection
            cursor.execute("SELECT password FROM mobile_app_users WHERE emailAddress = %s", (_email,))
            
            result = cursor.fetchone()
            app.logger.info(result)
            if result is not None:
                # jsonify returns a response
                if check_password(result[0],_password):
                    result = jsonify({"success":"login successful"})
                else:
                    result = jsonify({"error":"login unsuccessful"})
                return result
            else:
                return jsonify({"error":"login unsuccessful"})

        else:
            return jsonify({"error":"parameters cannot be empty"})
        cursor.close()
    except KeyError:
        app.logger.warn('The data was malformed')
        return jsonify({"error":"parameters cannot be empty"})


# doesn't interact with the database yet.
@app.route('/register', methods=['POST']) #data is submitted
def register():
    try:
        #POST - request.args - URL parameters
        _email = request.form['email'] 
        _username = _email.rsplit('@', 1)[0]
        _password = request.form['password']
        _passwordConfirm = request.form['password_confirm']
        
        if _password == _passwordConfirm:
            cursor = conn.cursor()
            # stored passwords must be hashed
            password_hash = hash_password(_password)
            cursor.execute("INSERT INTO mobile_app_users (emailAddress,password,username) values (%s,%s,%s)", (_email, password_hash, _username))
            conn.commit()
            return jsonify({"success":"registration confirmed"})
        else:
            return jsonify({"error":"passwords do not match"})
    except KeyError:
        app.logger.warn('invalid inputs')
        return jsonify({"error":"invalid inputs"})

if __name__ == "__main__":
    #app.run() #local
    # http://10.0.0.6:5000
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True) #reloads
