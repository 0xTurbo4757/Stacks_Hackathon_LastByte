#Check for same users
#Generate Hash
#Store hash
import hashFunction
import socket
import json
import random
from threading import Thread

class Client:
    UDP_DATA_BUFFER_SIZE = 8192
    DATA_ENCODING_FORMAT = "utf-8"

    def __init__(self,username):
        self.BlockChain = []

        #Socket Handeling
        self.ClientForMarket_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.ClientForMarket_Socket.bind(("localhost", 1234))
        self.ClientForMarket_Socket.connect(("localhost", 2600))

        self.type = ""
        self.username = username

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

        (public_key_str,private_key_str,self.pem) = hashFunction.rsa_genkey()
        self.pubkey = public_key_str
        self.privkey = private_key_str
        self.pubkeyf = self.pem.public_key()

        entry = {"username": username,"pubkey":public_key_str,"privkey":private_key_str ,"type":self.type ,"hashed_username":hashed_username}

        
        json.dump (entry,f)
        f.write("\n")
        f.close()


    def send_to_server(self,data):
        self.ClientForMarket_Socket.sendto(str(data).encode("utf-8"), ("localhost",2600))

    def recv(self):
        try:
            incomming_UDP_Data = self.ClientForMarket_Socket.recvfrom(Client.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(Client.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            return ("", "")
        #EndTry

    def view_orderbook(self):
        data = "order"
        self.send_to_server(data)
        data,addr = self.recv()
        print("OrderBook: \n{}".format(data))

    #SOCKET
    def Get_Data_from_Miner(self):
        try:
            incomming_UDP_Data = self.ClientForMiner_Socket.recvfrom(Client.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(Client.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            return ("", "")
        #EndTry
    #EndFunction

    #OK
    def Get_BlockChain_Size(self):
        return len(self.BlockChain)
    #EndFunction

     #OK
    def Extract_Data_from_BlockChain_BlockData(self, target_block_data):
        sender_addr = ""
        receiver_addr = ""
        ammount_transfered = ""
        commas = 0

        for current_char in target_block_data:
            if (current_char == ','):
                commas += 1
                continue
            #EndIf

            if (commas == 0):
                sender_addr += current_char
            #EndIf

            if (commas == 1):
                receiver_addr += current_char
            #EndIf

            if (commas == 2):
                ammount_transfered += current_char
            #EndIf
        #EndFor

        #Return Extracted Data as tuple
        return ((sender_addr, receiver_addr, ammount_transfered))
    #EndFunction

     #OK
    # Iterates through Blockchain to get latest Balance of the merchant
    def Get_Merchant_Current_Balance(self, merchant_public_key):

        balance_given_to_merchant = 0
        balance_taken_from_merchant = 0
        net_merchant_balance = 0
        
        #Iterate thru entire chain for balance given to merchant
        for current_block_iterator in range(1, (self.Get_BlockChain_Size() + 1)):

            #Get Current Block as JSON obj
            current_block = self.BlockChain[str(current_block_iterator)]

            #Extract Data out of current block
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block["Data"])

            #If Merchant Recieved Funds
            if (receiver_key == merchant_public_key):
                print("Merchant {} received {} from {}".format(receiver_key, amount_transfered, sender_key))
                balance_given_to_merchant += int(amount_transfered)
            #EndIf
        #EndFor

        #Iterate thru entire chain for balance taken from merchant
        for current_block_iterator in range(1, (self.Get_BlockChain_Size() + 1)):

            #Get Current Block as JSON obj
            current_block = self.BlockChain[str(current_block_iterator)]

            #Extract Data out of current block
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block["Data"])

            #If Merchant Sent Funds
            if (sender_key == merchant_public_key):
                print("Merchant {} Sent {} from {}".format(sender_key, amount_transfered, receiver_key))
                balance_taken_from_merchant += int(amount_transfered)
            #EndIf
        #EndFor

        #Calculate Net Merchant Balance
        net_merchant_balance = (balance_given_to_merchant - balance_taken_from_merchant)

        #Return net balance
        return net_merchant_balance
    # EndFunction

    def Handle_Incoming_BlockChain_from_Miner_THREADED(self):
        while True:
            BlockChain_Data_RAW, Miner_Address = self.Get_Data_from_Miner()
            if (len(BlockChain_Data_RAW)):
                #print("Received BlockChain {}".format(BlockChain_Data_RAW))
                Updated_BlockChain = json.loads(json.dumps(BlockChain_Data_RAW))
                print("Received BlockChain:\n")
                #self.Print_JSON_Object(Updated_BlockChain)
                self.BlockChain = Updated_BlockChain
            #EndIf
        #EndWhile
    #EndFunction

# c1 = Client("Bob")

def foo():
    return "NULL"

def sell():
    item = str(input("Item name : "))
    price = str(input("Price for selling : "))
    #Create signature#############################
    n= str(random.randint(1,1000))
    n=c1.username+n
    hashh = hashFunction.getSHA(n,5)

    sign = hashFunction.generate_signature(hashh,c1.pem)

    if (hashFunction.verify_signature(sign,hashh,c1.pubkeyf)):
        print("Signature Verified from public key")
    else:
        print("Cannot Verify")

    ##########################################
    data = {"item": item,"price":price ,"pubkey":c1.pubkey,"type":c1.type}
    data = str(data)
    c1.send_to_server(data)

def buy():
    item = str(input("Item name : "))
    price = str(input("Price for buying : "))
    #Create signature#############################
    n= str(random.randint(1,1000))
    n=c1.username+n
    hashh = hashFunction.getSHA(n,5)

    sign = hashFunction.generate_signature(hashh,c1.pem)

    if (hashFunction.verify_signature(sign,hashh,c1.pubkeyf)):
        print("Signature Verified from public key")
    else:
        print("Cannot Verify")

    ##########################################


    data = {"item": item,"price":price , "pubkey":c1.pubkey,"type":c1.type}
    data = str(data)    
    c1.send_to_server(data)
    

while True:
    try:
        usrname = str(input("Enter username : "))
        c1 = Client(usrname)
        
        break
    except Exception as e:
        print (e)
        print("Can't use this username : Already exist (Public key clash)")
    


Client_BlockChain_Update_THREAD = Thread(target=c1.Handle_Incoming_BlockChain_from_Miner_THREADED)
Client_BlockChain_Update_THREAD.daemon = True
Client_BlockChain_Update_THREAD.start()

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
            c1.view_orderbook()
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
            c1.view_orderbook()
        if (temp == 4):
            print(c1.pubkey + "\n")
        if (temp == 5):
            print(c1.privkey+ "\n")
        if (temp == 6):
            print("\n"*100)

