from flask import Flask, render_template
from flask import jsonify
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')
	
@app.route('/test-api')
def api():
    return jsonify(msg="This is a json msg")

if __name__ == "__main__":
    #app.run()
	app.run(debug=True) #reloads