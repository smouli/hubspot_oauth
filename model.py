import requests, json, time
from flask.helpers import make_response
from requests.sessions import session
from config import * 

#redirect url Constant
redirectUrl = f"{client['authorize_endpoint']}?client_id={client['client_id']}&redirect_uri={client['redirect_uri']}&scope=oauth%20crm.objects.deals.read%20crm.objects.deals.write"

def next_account_num():

    collection = mongo_client_db['account_number']
    res = collection.find_one_and_update({}, {'$inc': {'account_num': 1}})
    if res is None:
        collection.insert_one({'account_num': 1})
        return '1'
    res = collection.find_one({})
    return str(res['account_num'])

def update_token_in_db(db_record):
    db_record['curr_time'] = int(time.time())
    collection = mongo_client_db['tokenData']

    query = {'account_num': db_record['account_num']}
    new_values = {"$set": {'token': db_record['token'], 'curr_time': db_record['curr_time']}}

    collection.update_one(query, new_values)


def store_token_to_db(tokenObj):    
    accountNum = next_account_num()

    #tokenObj['curr_time'] = int(time.time())

    token_info = {'account_num': accountNum, 'token': tokenObj, 'curr_time': int(time.time()), 'last_synced': 0}

    collection = mongo_client_db['tokenData']

    collection.insert_one(token_info)

    return accountNum

def validate_token(db_record):
    #check if token is valid
    #print(type(accessToken['expires_in']))
    if int(time.time()) > (int(db_record['curr_time']) + int(db_record['token']['expires_in'])):
        #if not get a new token with refresh token
        # with token make call to deals endpoint and return data
        refreshToken = db_record['token']['refresh_token']
        new_token = requests.post(client['token_endpoint'], headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}, data={'grant_type': 'refresh_token', 'client_id': client['client_id'], 'client_secret': client['client_secret'], 'redirect_uri': client['redirect_uri'], 'refresh_token': refreshToken})

        db_record['token'] = json.loads(new_token.text)
        update_token_in_db(db_record)
    
    return db_record['token']['access_token']

def sync_deals(access_token, account_num):
    
    last_updated = find_last_updated_deal_timestamp(account_num)
    
    response = requests.get(f"{client['recent_deals_endpoint']}?since={last_updated}", headers={'Authorization': f"Bearer {access_token}"})
    
    if response.status_code != 200:
        return None
    
    raw = json.loads(response.text)
    deal_data = []
    for result in raw['results']:
        dealObj = {}
        dealObj['accountid'] = account_num
        dealObj['dealId'] = result['dealId']
        dealObj['dealname'] = result['properties']['dealname']['value']
        dealObj['dealstage'] = result['properties']['dealstage']['value']
        dealObj['closedate'] = result['properties']['closedate']['value']
        dealObj['amount'] = result['properties']['amount']['value']
        dealObj['dealtype'] = result['properties']['dealtype']['value']
        deal_data.append(dealObj)

    write_deals_to_db(deal_data)
    #update the last updated timestamp
    update_last_updated_deal_timestamp(account_num)
    return response.text

def write_deals_to_db(deal_data):
    collection = mongo_client_db['dealsInfo']
    for deal in deal_data:
        collection.update_one({'accountid': deal['accountid'], 'dealId': deal['dealId']}, {'$set': deal}, upsert=True)
    

def find_last_updated_deal_timestamp(account_num):
    collection = mongo_client_db['tokenData']

    tokenObj = collection.find_one({'account_num': account_num})
    
    return tokenObj['last_synced']

def update_last_updated_deal_timestamp(account_num):
    collection = mongo_client_db['tokenData']
    collection.update_one({'account_num': account_num}, {'$set': {'last_synced': int(time.time() * 1000)}})

def read_deals_from_db(account_num):
   
    collection = mongo_client_db['dealsInfo']
    deals = collection.find({'accountid': account_num})
    ret_val = []
    for deal in deals: 
        del deal['_id']
        del deal['accountid']
        ret_val.append(deal)
    
    return json.dumps(ret_val, sort_keys = False, indent = 2)

def find_token_from_db(account_num):
    collection = mongo_client_db['tokenData']

    tokenObj = collection.find_one({'account_num': account_num})
    return tokenObj