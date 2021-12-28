import pymongo

client = {
    'authorize_endpoint': 'https://app.hubspot.com/oauth/authorize',
    'token_endpoint': 'https://api.hubapi.com/oauth/v1/token',
    'deals_endpoint': 'https://api.hubapi.com/deals/v1/deal/paged',
    'recent_deals_endpoint': 'https://api.hubapi.com/deals/v1/deal/recent/modified',
    # from app settings
    'client_id': '75da7f80-7317-4500-82bc-73fbcaba8f5e',
    'client_secret': 'cb3b2c18-e4ca-483c-a731-9cb7abfbc260',
    'redirect_uri': 'http://localhost:8000/callback'
}


db_creds = {
    'username': 'mainUser',
    'passwd': '4519Carol',
    'host': 'cluster0.eebau.mongodb.net',
}


def connect_to_mongo():
    mongoClient = pymongo.MongoClient(f"mongodb+srv://{db_creds['username']}:{db_creds['passwd']}@{db_creds['host']}/dealsData?retryWrites=true&w=majority")
    print("connected to mongo")
    db = mongoClient['dealsData']
    return db

mongo_client_db = connect_to_mongo()

