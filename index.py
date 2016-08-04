from flask import Flask, render_template, request, Response
from flask import jsonify
app = Flask(__name__)

@app.route('/')
def main():
    app.logger.debug('Requested')
    return render_template('index.html')

@app.route('/get-api', methods=['GET']) #get a resource
def getApi():
    id = request.args.get('id')     #GET - request.args - URL parameters
    msg = request.args.get('message')
    response = "Parmeters received %s, %s  " % (id, msg)
    print(response)
    return (response)

@app.route('/login', methods=['POST']) #data is submitted
def login():
    try:
        _email = request.form['email'] #POST - request.args - URL parameters
        _password = request.form['pass']
        # print("Parmeters received %sa, %s  " % (id, msg))
        # validate the received values
        if _email and _password:
            return 'Successful login', 200
        else:
            return 'Email and password must be submitted', 500
    except KeyError:
        print ("The data was malformed")
        app.logger.warn('The data was malformed')
        return 'Email and password must be submitted', 500

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


    #return jsonify(msg)


if __name__ == "__main__":
    #app.run() #local
	app.run(debug=True) #reloads
	#app.run(host='0.0.0.0') #publicly available
