from flask import Flask, render_template, request, redirect
from model import *
from config import * 

app = Flask(__name__)


@app.route("/")
def main():
    return redirect("/home")

# Overall design
# When the user visits /home, it checks to see if the cookie account_num contains a valid account number.
# If it does, we use the account number in mongo db to find the auth token of the corresponding Hubspot account. 
# I then fetch the deals, write it into mongo db and then display the deals to the user.
# If the account number is not valid, we generate a new account number, redirect the user to hubspot to link a hubspot test account 
# and store the auth info in mongo db with the account numnber and return it as a cookie.

@app.route("/home", methods=['GET'])
def home():
    account_num = request.cookies.get('account_num')

    if (account_num):
        tokenObj = find_token_from_db(account_num)
        if tokenObj is None:
            return '<h1>Did not find a Hubspot linked account</h1>'

        #check if token is valid
        #if not get a new token with refresh token
        access_token = validate_token(tokenObj)
        #Sync latest deals
        ret = sync_deals(access_token, account_num)
        if ret is None:
            print("Error in sync_deals")

        #Return latest deals to user
        response = read_deals_from_db(account_num)

        return render_template('index.html', response=response)

    else: 
        # if cookie does not exist, there is no token for this user. make a redirect to hubspot to get a token
        #After a token is received, store it in mongo and return a new cookie to the browser
        response = redirect(redirectUrl, code = 302)
        return response
    
    

@app.route("/callback", methods=['GET'])
def callback():

    code = request.args.get('code')
    token = requests.post(client['token_endpoint'], headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}, data={'grant_type': 'authorization_code', 'client_id': client['client_id'], 'client_secret': client['client_secret'], 'redirect_uri': client['redirect_uri'], 'code': code})
    
    account_num = store_token_to_db(json.loads(token.text))

    response = make_response(redirect("/home"))
    response.set_cookie('account_num', account_num)
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000,debug=True)