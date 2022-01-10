from flask import Flask, request, jsonify, render_template, redirect, url_for,session
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.secret_key = ""

client = pymongo.MongoClient("mongodb+srv://tempGod:tempGod@thehive.wexmn.mongodb.net/hive?retryWrites=true&w=majority")
db = client.hive
ident = db.ids
login_base = client.login 
login_handler = login_base.info 


@app.route('/setTemp/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)
    temp = request.args.get("temperature",None)
    
    # For debugging
    print(f"got name {name}")

    rebound = {}
    parcel = {"string": name, "temperature": temp}


    # Check if user sent a name at all
    if not name:
        rebound["ERROR"] = "Error occured check request."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        rebound["ERROR"] = "Error occured check request."
    # Now the user entered a valid name
    else:
        rebound["MESSAGE"] = f"Set {name} temperature to {temp} "
    print(rebound)
    query = {"string": name}
    comparison = ident.find_one(query)
    updatequery = {"$set": {"temperature" : temp}}
    print(comparison)

    #Experimental multi-tempstore code

    package_new = {"string": name, "temperature" : temp, "temperature2": 0, "temperature3" : 0}


    # Return the response in json format
    if not comparison:
        package_new = {"string": name, "temperature" : temp, "temperature2": 0, "temperature3" : 0}
        ident.insert_one(package_new)
    else:
        holderObj = {} 
        personObj = ident.find_one(query)

        holderObj['one'] = personObj['temperature']
        holderObj['two'] = personObj['temperature2']
        
        personObj['temperature'] = temp
        del personObj['_id']
        updatequery = {"$set": {"temperature" : temp, "temperature2" : holderObj['one'], "temperature3" : holderObj['two']}}
        ident.update_one(query,updatequery)
    return jsonify(updatequery)

# A welcome message to test our server
@app.route('/')
def home(): 
    return "<h1>Welcome to the temperature sense page</h1> <br> <h2>navigate to login</h2>"

@app.route('/user', methods=['GET', 'POST'])
def internal():
    try:
        if session['login_state'] == True:
            print("Passthrough")
            print(session['user_id'])
            return render_template('insidenew.html', username = session['user_id'])
    except:
        return "<h1>Unauthorized!!! Please Login</h1>"

@app.route('/getTemp/', methods=['GET'])
def demonstrate():
    idnum = request.args.get("idnum", None)
    tempSend = ident.find_one({"string":idnum})
    del tempSend['_id']
    return jsonify(
        tempSend
        )
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        userName = request.form['username']
        pwd = request.form['password']
        loginQuery = {"username" : userName, "password" : pwd}
        authenticateUser = login_handler.find_one(loginQuery)
        if not authenticateUser:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['login_state'] = True
            session['user_id'] = userName
            return redirect(url_for('internal'))
    return render_template('loginpage.html', error=error)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
