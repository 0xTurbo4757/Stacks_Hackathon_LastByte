#Check for same users
#Generate Hash
#Store hash
import hashFunction
import rsa # RSA Encryption
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
               

        
        # Store into json file
        f = open("clients.json","a")
        entry = {'username': username,'hashed_username':hashed_username}
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
        print("Can't use this username : Already exist (Public key clash)")
