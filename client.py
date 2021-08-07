#Check for same users
#Generate Hash
#Store hash
import hashlib # For SHA256
import rsa # RSA Encryption
import random # For random to generate key pair
import json

class Client:

    def __init__(self,username):
        # Buyer or Seller
        self.type = ""


        # Hash the username
        hsh = hashlib.sha256()
        busername = bytes(username,"utf-8")
        hashed_username = hsh.update(busername)
        hashed_username = hsh.digest()
        #print(hsh.hexdigest())




        # # Check from Json file
        # Loop until end of file
        f = open("clients.json","r")
        for line in f:
            
            temp = json.loads(line)

            if temp["hashed_username"] == hsh.hexdigest():
                raise Exception("Duplicate username")

        f.close()
               

        
        # Store into json file
        f = open("clients.json","a")
        entry = {'username': username,'hashed_username':hsh.hexdigest()}
        f.write("\n")
        json.dump (entry,f)
        f.close()





    def main(self):
        print()


#c1 = Client("Bob")
while True:
    try:
        usrname = str(input("Enter username : "))
        c1 = Client(usrname)

    except Exception as e:
        print("Can't use this username : Already exist (Public key clash)")
