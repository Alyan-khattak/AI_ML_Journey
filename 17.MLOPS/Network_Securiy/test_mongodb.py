## ═══════════════════════════════════════════════════════════════════
## pushdata.py — MongoDB Atlas Connection Test
## ═══════════════════════════════════════════════════════════════════
##
## HOW TO GET CONNECTION URI:
## 1. mongodb.com → Login → Your Project
## 2. Left Sidebar → Database → Clusters
## 3. Cluster0 → Connect button
## 4. Drivers → Python → Version 3.12+
## 5. "View full code sample" → copy URI
##    Format: mongodb+srv://username:password@cluster0.xxx.mongodb.net/
##
## HOW TO GET/CHANGE PASSWORD:
## 1. Left Sidebar → Quick Start → tumhara password wahan hai
##    OR
## 2. Security → Database Access → Edit user → Change Password
##    → Update User → wait 1 minute
##
## HOW TO WHITELIST YOUR IP:
## 1. Security → Network Access → Add IP Address
## 2. IP Address: 0.0.0.0/0  (allow from anywhere)
## 3. Description: allow all
## 4. Confirm
## ═══════════════════════════════════════════════════════════════════


## I got this Code from MogoDb Altlas 
## in the UI 'Left sideBar there is Database DropDown" 
## In there Select Clusters you will see ur cluster 
## There on ur cluster there will be a button sayig connect press that 
## A menu will open ... in There Selct Drivers on next page n driver select "python" and verson
## there will be a button view full code sample press that and 'll get this code 

## To get password On the left side bar theere Click Quick Start and youll see you pass



from pymongo import MongoClient
import certifi
from pymongo import MongoClient

#to import uri from .env file 
from dotenv import load_dotenv
import os

load_dotenv() # ← .env file load karo
MONGO_ATLAS_URI = os.getenv("MONGO_ATLAS_URI")

uri = MONGO_ATLAS_URI

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
