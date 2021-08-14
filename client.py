import socket
import json
import time
import hashFunction
import random
from threading import Thread
from ast import literal_eval
from os import system

class Client:

# --------------------------------- CONSTANTS

    MINER_BLOCKCHAIN_REQUEST_STR = "chain"                      #When this is sent to the miner, it sends the BlockChain Back
    CLIENT_ORDERBOOK_REQUEST_STR = "order"                      #When this is sent to the market, it sends the OrderBook Back
    DATA_ENCODING_FORMAT = "utf-8"                              #Data Encoding format for socket programming
    UDP_DATA_BUFFER_SIZE = 8192                                 #UDP Incomming data buffer size
    NEW_MERCHANT_FUND_AMOUNT = 100                              #Funds given to new merchants
    MINER_DEFAULT_ADDRESS = 0                                   #Default miner address

    USERDATABASE_FILE_NAME = "clients.json"                     #Filename of UserDataBase file
    
    MERCHANT_USERNAME_STR = "m_Username"                        #JSON KEY: Merchant User Name
    MERCHANT_HASHED_USERNAME_STR = "m_HashedUsername"           #JSON KEY: Merchant Hashed User Name
    MERCHANT_PRIVATE_KEY_STR = "m_PrivKey"                      #JSON KEY: Merchant Private Key
    MERCHANT_PUBLIC_KEY_STR = "m_PubKey"                        #JSON KEY: Merchant Public Key
    MERCHANT_SIGNATURE_STR = "m_Sign"                           #JSON KEY: Merchant Signature
    MERCHANT_TYPE_STR = "m_Type"                                #JSON KEY: Merchant Type
    MERCHANT_COMODITY_STR = "m_Item"                            #JSON KEY: Merchant Item to sell/buy
    MERCHANT_PRICE_STR = "m_Price"                              #JSON KEY: Merchant Item Price
    MERCHANT_TYPE_BUYER_STR = "B"                               #JSON VAL: Merchant Type: Buyer
    MERCHANT_TYPE_SELLER_STR = "S"                              #JSON VAL: Merchant Type: Seller

# --------------------------------- CONSTRUCTOR

    def __init__(self, market_ip, market_port, miner_ip, miner_port):

        # Socket Handling As Client For market.py
        self.ClientForMarket_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMarket_SocketAddr = (market_ip, market_port)
        self.ClientForMarket_Socket.connect(self.ClientForMarket_SocketAddr)

        #self.ClientForMarket_Socket.settimeout(None)
        #self.ClientForMarket_Socket.bind(('', random.randint(10000, 50000)))

        # Socket Handling As Client For miner.py
        self.ClientForMiner_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMiner_SocketAddr = (miner_ip, miner_port)
        self.ClientForMiner_Socket.connect(self.ClientForMiner_SocketAddr)

        #Client Data
        self.Current_Client_Type = ""
        self.Current_Client_Username = ""
        self.Current_Client_HashedUsername = ""
        self.Current_Client_Public_Key = ""
        self.Current_Client_Private_Key = ""
        self.Current_Client_Public_Key_PEM = ""

        #Client Class Globals
        self.OrderBook = []         # has dictionaries at each index

        self.BlockChain = {}        # Entire BlockChain as dictionary
    #EndFunction

# --------------------------------- MERCHANT

    #Blockchain traverse to get final balance of given Public Address
    def Get_Merchant_Current_Balance(self, merchant_public_key):

        balance_given_to_merchant = 0
        balance_taken_from_merchant = 0
        net_merchant_balance = 0

        #print("\n[INFO]: Current BlockChain is {}\n\n Its Size is: {}\n".format(self.BlockChain, self.Get_BlockChain_Size()))

        if (self.Get_BlockChain_Size() == 0):
            print("\n[INFO]: You haven't been assigned initial funds from the miner")
            return 0
        #EndIf
        
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

# --------------------------------- SOCKET RECEIVE
    
    #Receives Data from Market
    def Get_Data_from_Market(self):
        try:
            incomming_UDP_Data = self.ClientForMarket_Socket.recvfrom(Client.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(Client.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            #print("\nException During Market Data Read: {}\n".format(e))
            return ("", "")
        #EndTry
    #EndFunction
    
    #Receives Data from Miner
    def Get_Data_from_Miner(self):
        try:
            incomming_UDP_Data = self.ClientForMiner_Socket.recvfrom(Client.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(Client.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            return ("", "")
        #EndTry
    #EndFunction

# --------------------------------- SOCKET SEND
    
    #Encodes Data and sends to Market
    def Send_Data_to_Market(self, data_to_send):
        #self.ClientForMarket_Socket.connect(self.ClientForMarket_SocketAddr)
        self.ClientForMarket_Socket.sendto(
            str(data_to_send).encode(Client.DATA_ENCODING_FORMAT),
            self.ClientForMarket_SocketAddr
        )
    #EndFunction

    #Encodes Data and sends to Miner
    def Send_Data_to_Miner(self, data_to_send):
        self.ClientForMiner_Socket.sendto(
            data_to_send.encode(Client.DATA_ENCODING_FORMAT), 
            self.ClientForMiner_SocketAddr
        )
    #EndFunction

# --------------------------------- UPDATERS
    
    def Update_Current_OrderBook(self, new_orderbook):
        self.OrderBook = list(new_orderbook)
    #EndFunction

    #
    def Update_Current_BlockChain(self, new_block_chain):
        self.BlockChain = dict(new_block_chain)
    #EndFunction

# --------------------------------- REQUESTS

    #Requests market to send latest OrderBook
    #This function is used in threading for constant update of OrderBook
    def Request_Latest_OrderBook_from_Market(self):
        self.Send_Data_to_Market(Client.CLIENT_ORDERBOOK_REQUEST_STR)
    #EndFunction

    #Requests miner to send latest BlockChain
    #This function is used in threading for constant update of BlockChain
    def Request_Latest_BlockChain_from_Miner(self):
        self.Send_Data_to_Miner(Client.MINER_BLOCKCHAIN_REQUEST_STR)
    #EndFunction

# --------------------------------- CONSOLE 
    
    def Console_ClearScreen(self):
        system("cls")
    #EndFunction

    def Console_Pause(self):
        print("\n")
        system("pause")
    #EndFunction

    def Console_Delay(self, time_s):
        time.sleep(time_s)
    #EndFunction

# --------------------------------- HANDLERS

    #Username Validation
    def Handle_New_User(self):
        #Get Current User name
        self.Current_Client_Username = self.Get_Valid_Username_from_User()
        
        #Get Current User type
        self.Current_Client_Type = self.Get_Valid_UserType_from_User()

        #Generate User's Public & Private Key
        self.Generate_User_RSA_Keys()
        
        #Save all current Client details into UserDataBase
        self.Update_UserDataBase_File()

        print("\nUser Succesfully Registered!\n")

        self.Console_Delay(1)
    #EndFunction

    #Place bid on the Market
    def Handle_Market_Buy_Sell_Operation(self):
        self.Send_Data_to_Market(self.Get_Signed_Request_Message_for_Market())
    #EndFunction

    #Main Menu Handler
    def Handle_Main_Menu(self):
        while True:

            #Request Miner To Send Latest BlockChain
            #Received BlockChain asynchronously updated using threads
            self.Request_Latest_BlockChain_from_Miner()

            #Request Market To Send Latest OrderBook
            #Received OrderBook asynchronously updated using threads
            self.Request_Latest_OrderBook_from_Market()

            self.Console_ClearScreen()

            # Menu 
            print("       Main Menu\n")
            print("1. View Current balance")
            if (self.Current_Client_Type == "S"):
                print("2. Sell something")
            else:
                print("2. Buy something")
            #EndIf
            print("3. View Orderbook")
            print("4. View Current BlockChain")
            print("5. Show Your Current Public Key")
            print("6. Show Your Current Private Key")
            print("7. Clear Screen")
            print("8. Logout")
            print("9. Exit")

            try:
                UserInput_Choice = int(input("\nEnter Choice Here: "))
            except:
                print("Please input only integers!")
                self.Console_Delay(2)
                self.Console_ClearScreen()
                continue
            #EndTry

            #View Current balance
            if (UserInput_Choice == 1):

                print("\nYour Current Balance is: {}".format(self.Get_Merchant_Current_Balance(self.Current_Client_Public_Key)))

            #Buy/Sell Something
            if (UserInput_Choice == 2):

                self.Handle_Market_Buy_Sell_Operation()
            
            #View Orderbook
            if (UserInput_Choice == 3):

                self.Print_OrderBook()
            
            #View Current BlockChain
            if (UserInput_Choice == 4):

                self.Print_BlockChain()

            #Show Your Current Public Key
            if (UserInput_Choice == 5):

                print("\nYour Current Public Key is: \n\n{}".format(self.Current_Client_Public_Key))

            #Show Your Current Private Key
            if (UserInput_Choice == 6):

                print("\nYour Current Private Key is: \n\n{}".format(self.Current_Client_Private_Key))

            #Clear Screen
            if (UserInput_Choice == 7):

                self.Console_ClearScreen()
                continue

            #Logout
            if (UserInput_Choice == 8):

                self.Console_ClearScreen()
                break
            
            #Exit
            if (UserInput_Choice == 9):

                exit()
            
            #EndIf

            self.Console_Pause()
        #EndWhile
    #EndFunction

# --------------------------------- THREADED HANDLERS
    
    def Handle_Incoming_BlockChain_from_Miner_THREADED(self):
        while True:
            print("\nAttempting Data Read From Miner..")
            BlockChain_Data_RAW, Miner_Address = self.Get_Data_from_Miner()
            
            if (len(BlockChain_Data_RAW)):

                #Updated_BlockChain = json.loads(json.dumps(BlockChain_Data_RAW))
                Updated_BlockChain = literal_eval(BlockChain_Data_RAW)
                
                #print("\nReceived BlockChain:")
                #self.Print_JSON_Object(Updated_BlockChain)
                self.Update_Current_BlockChain(Updated_BlockChain)
            
            #EndIf
        #EndWhile
    #EndFunction

    def Handle_Incoming_OrderBook_from_Market_THREADED(self):
        while True:
            print("\nAttempting Data Read From Market..")
            OrderBook_Data_RAW, Market_Addr = self.Get_Data_from_Market()

            if (len(OrderBook_Data_RAW)):
                print("Received: '{}' from 'localhost:{}'".format(OrderBook_Data_RAW, Market_Addr[1]))

                Updated_OrderBook = literal_eval(OrderBook_Data_RAW)

                self.Update_Current_OrderBook(Updated_OrderBook)

            #EndIf
        #EndWhile
    #EndFunction

# --------------------------------- USER

    #Checks for duplicate PublicKey
    #Loops until unique PublicKey is obtained from Username
    #Checks the Json file for Data regarding keys
    def Get_Valid_Username_from_User(self):
        final_username = ""                 #Valid Username

        #Try to Open User DataBase File
        try:
            UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "r")
        except (FileNotFoundError):
            #No File exists
            print("\n[INFO]: UserDataBase file '{}' doesnt exist!\nMaking a new one...\n".format(Client.USERDATABASE_FILE_NAME))

            #Create the file
            NEW_UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "w")
            #Close it immediately because we dont want to write any data to it
            NEW_UserDataBaseFile.close()

            #Try opening the file again
            try:
                UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "r")
            except Exception as e:
                #This shouldnt have happened
                print("\n[ERROR]: {} Attempted to create UserDataBase file '{}' failed!!\nExact Error: {}\nExiting\n".format(Client.USERDATABASE_FILE_NAME, e))
                #We cant continue, we needa die :(
                exit()
            #EndTry
        #EndTry

        #Keep inputting from user until valid username is obtained
        while True:
            #Found Flag
            valid_username_found = True         

            #Get Username from user
            final_username = str(input("\nEnter Your Name Here: "))

            #Get Hash of the target Username
            target_hashed_username = self.Get_Hashed_Username(final_username)

            #Iterate through database to check if username already exists
            for current_line in UserDataBaseFile:
                current_user_entry_JSON = json.loads(current_line)
                if current_user_entry_JSON[Client.MERCHANT_HASHED_USERNAME_STR] == target_hashed_username:
                    valid_username_found = False
                    break
                #EndIf
            #EndFor

            if (valid_username_found):
                #Save Final Username Hash
                self.Current_Client_HashedUsername = target_hashed_username

                #GTFO!
                break
            else:
                print("\n[ERROR]: Can't use this Username!\nAlready exists (Public key clash)\nPlease Choose another Username\n")
            #EndIf
        #EndWhile

        #Close The File
        UserDataBaseFile.close()

        #Return the valid Username
        return final_username
    #EndFunction

    #Get User Type (Buyer or Seller) From User
    def Get_Valid_UserType_from_User(self):
        input_usertype = str(input("\nEnter 'B' if you're a Buyer or 'S' if a Seller: "))
        
        while (input_usertype != "B" and input_usertype != "S"):
            print("\n[ERROR]: Enter 'B' or 'S' only!")
            input_usertype = str(input("\nEnter 'B' if you're a Buyer or 'S' if a Seller: "))
        #EndWhile

        #Return UserType
        return input_usertype
    #EndFunction

    #Generate Current User's RSA Keys
    def Generate_User_RSA_Keys(self):
        self.Current_Client_Public_Key, self.Current_Client_Private_Key, self.Current_Client_RSA_KEY_OBJ = hashFunction.rsa_genkey()
        self.Current_Client_Public_Key_PEM = self.Current_Client_RSA_KEY_OBJ.public_key()
    #EndFunction

    #Write Userinfo onto the UserDataBase JSON file
    def Update_UserDataBase_File(self):
        # Store into json file
        UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "a")

        Database_Entry = {
            Client.MERCHANT_USERNAME_STR : self.Current_Client_Username,
            Client.MERCHANT_HASHED_USERNAME_STR : self.Current_Client_HashedUsername,
            Client.MERCHANT_PUBLIC_KEY_STR : self.Current_Client_Public_Key,
            Client.MERCHANT_PRIVATE_KEY_STR : self.Current_Client_Private_Key,
            Client.MERCHANT_TYPE_STR : self.Current_Client_Type,
        }

        #Write to file
        json.dump(Database_Entry, UserDataBaseFile)

        #Add new line
        UserDataBaseFile.write("\n")

        #Save file & close
        UserDataBaseFile.close()
    #EndFunction

# --------------------------------- DIGITAL SIGNATURE
    
    def Get_Digital_Signature_using_PrivateKey(self, target_message):
        #n = str(random.randint(1,1000))
        #n = self.Current_Client_Username + n
        #hashh = hashFunction.getSHA(n,5)

        return hashFunction.generate_signature(target_message, self.Current_Client_RSA_KEY_OBJ)
    #EndFunction

    def Verify_Digital_Signature_using_PublicKey(self, target_signature, target_message):
        if (hashFunction.verify_signature(target_signature, target_message, self.Current_Client_Public_Key_PEM)):
            print("Signature Verified from public key")
            return True
        else:
            print("Cannot Verify")
            return False
        #EndIf
    #EndFunction
    
    def Get_Signed_Request_Message_for_Market(self):
        Final_Signed_Market_Request_Message = {}

        UserInput_Item_Name = str(input("Enter Your Item name Here: "))
        UserInput_Item_Price = str(input("Enter Price For the Item Here: "))

        #BACKUP
        Market_Request_Message_String = "{\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\"}" % (
            Client.MERCHANT_COMODITY_STR,
            UserInput_Item_Name,
            Client.MERCHANT_PRICE_STR,
            UserInput_Item_Price,
            Client.MERCHANT_PUBLIC_KEY_STR,
            self.Current_Client_Public_Key,
            Client.MERCHANT_TYPE_STR,
            self.Current_Client_Type
        )

        # Market_Request_Message_Dict = {
        #     Client.MERCHANT_COMODITY_STR : UserInput_Item_Name,
        #     Client.MERCHANT_PRICE_STR : UserInput_Item_Price,
        #     Client.MERCHANT_PUBLIC_KEY_STR : self.Current_Client_Public_Key,
        #     Client.MERCHANT_TYPE_STR : self.Current_Client_Type
        # }

        #Signature = (self.Get_Digital_Signature_using_PrivateKey(Market_Request_Message_Dict))

        #print("\nSending Signature: {}\n\nType: {}".format(Signature, type(Signature)))

        #print("\Decoded Signature: {}\n\nType: {}".format(hex(Signature), type(hex(Signature))))

        #BACKUP
        # Market_Request_Digital_Signature = "{\"%s\":\"%s\"}]" % (
        #     Client.MERCHANT_SIGNATURE_STR,
        #     Signature
        # )

        # Final_Signed_Market_Request_Message = {
        #     "m_msg" : Market_Request_Message_Dict,
        #     Client.MERCHANT_SIGNATURE_STR : Signature
        # }

        #print("Final Dict: \n{}\n".format(Final_Signed_Market_Request_Message))

        #Final_Signed_Market_Request_Message = Market_Request_Message_String + "," + Market_Request_Digital_Signature

        return Market_Request_Message_String
    #EndFunction

# --------------------------------- MISC

    #Function to return transcation info from a given block of the blockchain
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
    
    #Returns Blockchain Size
    def Get_BlockChain_Size(self):
        #print("BlockChain Blocks: {}".format(self.BlockChain.keys()))

        #len() on a dict returns number of top level keys in dict
        return len(self.BlockChain)
    #EndFunction

    #Print nice beutiful OrderBook
    def Print_OrderBook(self):

        if (len(self.OrderBook) == 0):
            print("\nThe order book is empty!")
            return
        # EndIf

        index = 1
        for current_order in self.OrderBook:
            print("\nMerchant {}".format(index))
            print("Merchant Type : {}".format(current_order[Client.MERCHANT_TYPE_STR]))
            print("Merchant Key  : {}".format(current_order[Client.MERCHANT_PUBLIC_KEY_STR]))
            print("Merchant Item : {}".format(current_order[Client.MERCHANT_COMODITY_STR]))
            print("Merchant Price: {}".format(current_order[Client.MERCHANT_PRICE_STR]))

            index += 1
        # EndFor
    #EndFunction

    #Print JSON object
    def Print_JSON_Object(self, target_object):
        print('\n', end='')

        print(json.dumps(target_object, indent=4, sort_keys=True))
        
        print('\n', end='')
    #EndFunction

    #Print BlockChain
    def Print_BlockChain(self):
        self.Print_JSON_Object(self.BlockChain)
        print("BlockChain Size: {}".format(self.Get_BlockChain_Size()))
    #EndFunction

    #Return the Hash of username
    def Get_Hashed_Username(self, target_username):
        return hashFunction.getSHA(target_username, 5)
    #EndFunction

# --------------------------------- RUN

    def RunClient(self):
        #Main loop
        while True:

            self.Handle_New_User()

            self.Handle_Main_Menu()

        #EndWhile
    #EndFunction

#EndClass

def main():
    market_ip = "localhost"
    miner_ip = market_ip
    client_for_market_port = 56000
    client_for_miner_port = 55000

    client = Client(market_ip, client_for_market_port, miner_ip, client_for_miner_port)
    
    #Threading For BlockChain Update
    Client_BlockChain_Update_THREAD = Thread(target=client.Handle_Incoming_BlockChain_from_Miner_THREADED)
    Client_BlockChain_Update_THREAD.daemon = True
    Client_BlockChain_Update_THREAD.start()

    #Threading For OrderBook Update
    Client_OrderBook_Update_THREAD = Thread(target=client.Handle_Incoming_OrderBook_from_Market_THREADED)
    Client_OrderBook_Update_THREAD.daemon = True
    Client_OrderBook_Update_THREAD.start()

    #Run The Client
    client.RunClient()
    # while True:

    #     print("\nSock Details: {}\n".format(client.ClientForMarket_Socket.getsockname()))
    #     client.Request_Latest_OrderBook_from_Market()
    #     client.Handle_Incoming_OrderBook_from_Market()
    #     client.Print_OrderBook()
    # #EndWhile
#EndMain

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nExiting Client\nGoodBye!\n")
        exit()
    #EndTry
#EndIf