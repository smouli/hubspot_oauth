# Hubspot Deals Application

Steps to run the application:
1. Unzip the files into a dir 
2. Run ``python server.py`` on the root directory. I ran it on python 3.8 
3. Navigate to localhost:8000 and the Deals should be displayed

#Architecture
Currently I am using a mongoDB atlas instance hosted on AWS. I have one database called dealsData and 3 collections inside it.
These are:
1. tokenData - Each time a new user gets authorized on Hubspot, a document is created. It stores the Access Token, Refresh Token, Token validity duration (Expires_in) and Token Type. In addition to these, it also stores a current timestamp of when the document was created and also the last_synced field, which is used when an api call is made to get the latest set of 
Deals modified/created on the Hubspot account. 

2. dealsInfo - Each time a new deal gets pulled in from the recent_deals_endpoint, a document is created. An account_id is stored with each deal as well. Each time the updated deals are returned, we want to search the database to update the document based on 2 fields, the account_number and the dealid. This was done since I am unsure if the dealid is unique across every deal in the hubspot account. The account_number maps to a access_token for an authorized user.

3. account_number - This stores a incrementing counter which is used as a unique identifier for each access token. The account_number is set as a cookie in the browser.

# Notes and things to improve upon
Deals/v1/paged - does not have since= param - would mean a lot more work to compare and update a deal. It might require to delete and write all the deals.

Deals/recent/modified - has since param which will return only modified deals. We just need to add into our db whatever it returns. 

Problem with using Deals/recent/modified is that it only reuturns 10k most recently modified deals. 

Feature to work on: Pagination - use offset field till hasmore is true. Pass the same offset value returned