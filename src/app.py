from flask import Flask,render_template,redirect,request,session
from web3 import Web3,HTTPProvider
import json
import os

import pyotp 
import qrcode 

app=Flask(__name__)
app.secret_key='1234'
app.config['UPLOAD_FOLDER']='src/static/uploads'

def connectWithBlockchain(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))

    if acc==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    
    artifact_path='./build/contracts/PasswordsManager.json'
    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']

    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3

def connectWithAuthenticator(name1):
    # Generate a random secret key
    secret_key = pyotp.random_base32()

    # Generate the provisioning URI
    totp = pyotp.totp.TOTP(secret_key)
    provisioning_uri = totp.provisioning_uri(name=name1, issuer_name='MakeSkilled')

    # Print the provisioning URI for debugging
    print("Provisioning URI:", provisioning_uri)

    # Path to save the QR code
    qr_code_directory = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes')
    os.makedirs(qr_code_directory, exist_ok=True)  # Create the directory if it doesn't exist
    qr_code_path = os.path.join(qr_code_directory, 'qr_code.png')

    # Generate and save the QR code
    qr_code = qrcode.make(provisioning_uri)
    qr_code.save(qr_code_path)

    # Return the secret key
    return secret_key

@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/collectData',methods=['GET','POST'])
def collectData():
    email=request.form['email']
    password=request.form['password']
    confirmpassword=request.form['confirmpassword']
    print(email,password,confirmpassword)

    if(password!=confirmpassword):
        return render_template('register.html',err='Passwords didnt match')
    else:
        session['username']=email
        session['password']=password
        secret_key=connectWithAuthenticator(email)
        session['secret_key']=secret_key

    return render_template('register2.html',image='uploads/qrcodes/qr_code.png')

@app.route('/collectData1',methods=['GET','POST'])
def collectData1():
    username=session['username']
    password=session['password']
    secret_key=session['secret_key']
    print(username,password,secret_key)

    if True:
        contract,web3=connectWithBlockchain(0)
        tx_hash=contract.functions.addUser(username,password,secret_key).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('register.html',res='Registration Successful')
    # except:
        # return render_template('register.html',err='Account Already Exist')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/storepassword',methods=['GET','POST'])
def storePassword():
    website=request.form['website']
    username=request.form['username']
    password=request.form['password']
    notes=request.form['message']
    print(website,username,password,notes)
    contract,web3=connectWithBlockchain(0)
    tx_hash=contract.functions.addPassword(session['username'],website,username,password,notes).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return render_template('dashboard.html',res='Password Stored')

@app.route('/loginform',methods=['GET','POST'])
def loginform():
    email=request.form['email']
    password=request.form['password']
    authenticatorcode=request.form['authenticatorcode']
    print(email,password,authenticatorcode)

    
    contract,web3=connectWithBlockchain(0)
    _usernames,_passwords,_secretkeys=contract.functions.viewUsers().call()

    for i in range(len(_usernames)):
        if(_usernames[i]==email and _passwords[i]==password):
            print(_secretkeys[i])
            totp = pyotp.TOTP(_secretkeys[i])
            if(totp.verify(int(authenticatorcode))):
                session['username']=email
                return redirect('/dashboard')

    return render_template('login.html',err='Invalid Login')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/contact')
def contactPage():
    return render_template('contact.html')

@app.route('/logout')
def logoutPage():
    session['username']=None
    return redirect('/')

@app.route('/mypasswords')
def mypasswords():
    data=[]
    contract,web3=connectWithBlockchain(0)
    _ids,_owners,_websitenames,_websiteusernames,_websitepasswords,_websitenotes=contract.functions.viewPasswords().call()

    for i in range(len(_ids)):
        if(_owners[i]==session['username']):
            dummy=[]
            dummy.append(_ids[i])
            dummy.append(_websitenames[i])
            dummy.append(_websiteusernames[i])
            dummy.append(_websitepasswords[i])
            dummy.append(_websitenotes[i])
            data.append(dummy)

    return render_template('mypasswords.html',l=len(data),dashboard_data=data)

@app.route('/update/<id>')
def update(id):
    print(id)
    session['id']=id
    contract,web3=connectWithBlockchain(0)
    _ids,_owners,_websitenames,_websiteusernames,_websitepasswords,_websitenotes=contract.functions.viewPasswords().call()

    for i in range(len(_ids)):
        if(_ids[i]==int(id)):
            websitename=_websitenames[i]
            websiteusername=_websiteusernames[i]
            websitepassword=_websitepasswords[i]
            websitenotes=_websitenotes[i]

    return render_template('updatepassword.html',websitename=websitename,websiteusername=websiteusername,websitepassword=websitepassword,websitenotes=websitenotes)

@app.route('/updatepassword',methods=['post'])
def updatepassword():
    owner=session['username']
    id=int(session['id'])
    website=request.form['website']
    username=request.form['username']
    password=request.form['password']
    notes=request.form['message']

    contract,web3=connectWithBlockchain(0)
    _ids,_owners,_websitenames,_websiteusernames,_websitepasswords,_websitenotes=contract.functions.viewPasswords().call()

    for i in range(len(_ids)):
        if(_ids[i]==int(id)):
            websitename=_websitenames[i]
            websiteusername=_websiteusernames[i]
            websitepassword=_websitepasswords[i]
            websitenotes=_websitenotes[i]

    if len(website)==0:
        website=websitename
    if len(username)==0:
        username=websiteusername
    if len(password)==0:
        password=websitepassword
    if len(notes)==0:
        notes=websitenotes

    tx_hash=contract.functions.updatePassword(id,website,username,password,notes).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/mypasswords')


@app.route('/delete/<id>')
def delete(id):
    print(id)
    contract,web3=connectWithBlockchain(0)
    tx_hash=contract.functions.deletePassword(int(id)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/mypasswords')

if __name__=="__main__":
    app.run(host='127.0.0.1',port=9001,debug=True)