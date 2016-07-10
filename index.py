from flask import Flask, render_template, request
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
    print("Parmeters received %s, %s  " % (id, msg))
    #return jsonify(msg)

@app.route('/post-api', methods=['POST']) #data is submitted
def postApi():
    try:
        id = request.form['id'] #POST - request.args - URL parameters
        msg = request.form['message']
        print("Parmeters received %s, %s  " % (id, msg))

    except KeyError:
        print ("The data was malformed")
        app.logger.warn('The data was malformed')

    #return jsonify(msg)


if __name__ == "__main__":
    #app.run() #local
	app.run(debug=True) #reloads
	#app.run(host='0.0.0.0') #publicly available
