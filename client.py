#Check for same users
#Generate Hash
#Store hash
import hashFunction
from cryptography.hazmat.primitives.asymmetric import rsa # RSA Encryption
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

import random # For random to generate key pair
import json

class Client:

    def __init__(self,username):
        # Buyer or Seller
        self.type = ""


        # Hash the username
        hashed_username = hashFunction.getSHA(username,5)




        # # Check from Json file
        # Loop until end of file
        f = open("clients.json","r")
        for line in f:
            
            temp = json.loads(line)

            if temp["hashed_username"] == hashed_username:
                raise Exception("Duplicate username")

        f.close()
               

        temp = str(input("Write 'B' for buyer, 'S' for seller :"))
        while (temp != "B" and temp != "S"):
            print("Error write only 'B' or 'S'")
            temp = str(input("Write 'B' for buyer, 'S' for seller :"))
        

        self.type = temp



        
        # Store into json file
        print("User Succesfully registered")
        f = open("clients.json","a")

        (public_key_str,private_key_str) = hashFunction.rsa_genkey()

        entry = {'username': username,'pubkey':public_key_str,'privkey':private_key_str ,'type':self.type ,'hashed_username':hashed_username}

        
        json.dump (entry,f)
        f.write("\n")
        f.close()





    def main(self):
        print()


# c1 = Client("Bob")
while True:
    try:
        usrname = str(input("Enter username : "))
        c1 = Client(usrname)

    except Exception as e:
        print (e)
        print("Can't use this username : Already exist (Public key clash)")
