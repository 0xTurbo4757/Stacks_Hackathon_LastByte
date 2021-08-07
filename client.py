#Check for same users
#Generate Hash
#Store hash
import hashFunction
import socket
import json

class Client:

    def __init__(self,username):
        #Socket Handeling
        self.ClientForMarket_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.ClientForMarket_Socket.bind(("localhost", 2600))
        self.ClientForMarket_Socket.connect(("127.0.0.1", 2600))

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
        self.pubkey = public_key_str
        self.privkey = private_key_str

        entry = {'username': username,'pubkey':public_key_str,'privkey':private_key_str ,'type':self.type ,'hashed_username':hashed_username}

        
        json.dump (entry,f)
        f.write("\n")
        f.close()





    def main(self):
        print()


# c1 = Client("Bob")

def foo():
    return "NULL"

def sell():
    item = str(input("Item name : "))
    price = str(input("Price for selling : "))
    data = {'item': item,'price':price , 'pubkey':c1.pubkey,'type':c1.type}
    data = str(data)
    data = data.encode("utf-8")


    c1.ClientForMarket_Socket.sendall(data)

def buy():
    item = str(input("Item name : "))
    price = str(input("Price for buying : "))
    data = {'item': item,'price':price , 'pubkey':c1.pubkey,'type':c1.type}
    data = str(data)
    data = data.encode("utf-8")


    c1.ClientForMarket_Socket.sendall(data)




while True:
    try:
        usrname = str(input("Enter username : "))
        c1 = Client(usrname)
        
        break
    except Exception as e:
        print (e)
        print("Can't use this username : Already exist (Public key clash)")
    

while True:


    # Menu
    if (c1.type == "S"): # Seller
        print("Commands\n\
                1. View Current balance\n\
                2. Sell something\n\
                3. View Orderbook\n\
                4. Show public key\n\
                5. Show Private key\n\
                6. Clear Screen\n")
        try:
            temp = int(input())
        except:
            print("Please input only integers")
        if (temp == 1):
            print(foo())
        if (temp == 2):
            sell()
        if (temp == 3):
            print(foo())
        if (temp == 4):
            print(c1.pubkey)
        if (temp == 5):
            print(c1.privkey)
        if (temp == 6):
            print("\n"*100)

    if (c1.type == "B"): # Buyer
        print("Commands\n\
                1. View Current balance\n\
                2. Buy something\n\
                3. View Orderbook\n\
                4. Show public key\n\
                5. Show Private key\n\
                6. Clear Screen\n")
        try:
            temp = int(input())
        except:
            print("Please input only integers")
        if (temp == 1):
            foo()
        if (temp == 2):
            buy()
        if (temp == 3):
            foo()
        if (temp == 4):
            print(c1.pubkey + "\n")
        if (temp == 5):
            print(c1.privkey+ "\n")
        if (temp == 6):
            print("\n"*100)

