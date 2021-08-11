import hashFunction
import socket
import json
import random
import time
from threading import Thread
from os import system

class Client:
    MINER_BLOCKCHAIN_REQUEST_STR = "chain"                      #
    CLIENT_ORDERBOOK_REQUEST_STR = "order"                      #
    DATA_ENCODING_FORMAT = "utf-8"                              #
    UDP_DATA_BUFFER_SIZE = 8192                                 #
    NEW_MERCHANT_FUND_AMOUNT = 100                              #
    MINER_DEFAULT_ADDRESS = 0                                   #

    USERDATABASE_FILE_NAME = "clients.json"                     #
    
    MERCHANT_USERNAME_STR = "m_Username"                        #
    MERCHANT_HASHED_USERNAME_STR = "m_HashedUsername"           #
    MERCHANT_PRIVATE_KEY_STR = "m_PrivKey"                      #
    MERCHANT_PUBLIC_KEY_STR = "m_PubKey"                        #
    MERCHANT_SIGNATURE_STR = "m_Sign"                           #
    MERCHANT_TYPE_STR = "m_Type"                                #
    MERCHANT_COMODITY_STR = "m_Item"                            #
    MERCHANT_PRICE_STR = "m_Price"                              #
    MERCHANT_TYPE_BUYER_STR = "B"                               #
    MERCHANT_TYPE_SELLER_STR = "S"                              #

    def __init__(self, market_ip, market_port, miner_ip, miner_port):

        # Socket Handling As Client For market.py
        self.ClientForMarket_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMarket_SocketAddr = (market_ip, market_port)
        self.ClientForMarket_Socket.connect(self.ClientForMarket_SocketAddr)

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
        self.BlockChain = []        # Entire BlockChain
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

    # ----------------------------- SOCKET -----------------------------
    #SOCKET
    def Send_Data_to_Market(self, data_to_send):
        self.ClientForMarket_Socket.sendto(
            data_to_send.encode(Client.DATA_ENCODING_FORMAT),
            self.ClientForMarket_SocketAddr
        )
    #EndFunction

    #SOCKET
    def Get_Data_from_Market(self, sock_timout=None):
        try:
            self.ClientForMarket_Socket.settimeout(sock_timout)
            incomming_UDP_Data = self.ClientForMarket_Socket.recvfrom(Client.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(Client.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except Exception as e:
            print("\nException During Market Data Read: {}\n".format(e))
            return ("", "")
        #EndTry
    #EndFunction

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

    #SOCKET
    def Send_Data_to_Miner(self, data_to_send):
        self.ClientForMiner_Socket.sendto(
            data_to_send.encode(Client.DATA_ENCODING_FORMAT), 
            self.ClientForMiner_SocketAddr
        )
    #EndFunction

    def Update_Current_OrderBook(self, new_orderbook):
        self.OrderBook = new_orderbook
    #EndFunction

    #
    def Update_Current_BlockChain(self, new_block_chain):
        self.BlockChain = new_block_chain
    #EndFunction
    
    #
    def Request_Latest_OrderBook_from_Market(self):
        self.Send_Data_to_Market(Client.CLIENT_ORDERBOOK_REQUEST_STR)
        received_data, market_addr = self.Get_Data_from_Market(2.0)
        print("Received: '{}' from 'localhost:{}'".format(received_data, market_addr))
        if (len(received_data)):
            self.Update_Current_OrderBook(received_data)
        #EndIf
    #EndFunction

    #SOCKET
    def Request_Latest_BlockChain_from_Miner(self):
        self.Send_Data_to_Miner(Client.MINER_BLOCKCHAIN_REQUEST_STR)
    #EndFunction
    # ----------------------------- SOCKET -----------------------------

    def ClearScreen(self):
        system("cls")
    #EndFunction

    def Pause(self):
        system("pause")
    #EndFunction

    # ----------------------------- HANDLERS -----------------------------
    #
    def Handle_Main_Menu(self):
        while True:

            #Request Miner To Send Latest BlockChain
            #Received BlockChain asynchronously updated using threads
            self.Request_Latest_BlockChain_from_Miner()

            self.ClearScreen()

            # Menu 
            print("Commands")
            print("1. View Current balance")
            if (self.Current_Client_Type == "S"):
                print("2. Sell something")
            else:
                print("2. Buy something")
            #EndIf
            print("3. View Orderbook")
            print("4. Show public key")
            print("5. Show Private key")
            print("6. Clear Screen")
            print("7. Logout")
            print("8. Exit")

            try:
                UserInput_Choice = int(input())
            except:
                print("Please input only integers!")
                time.sleep(2)
                self.ClearScreen()
                continue
            #EndTry

            if (UserInput_Choice == 1):
                print(self.Get_Merchant_Current_Balance(self.Current_Client_Public_Key))
            if (UserInput_Choice == 2):
                self.Handle_Operation_Sell()
            if (UserInput_Choice == 3):
                self.Request_Latest_OrderBook_from_Market()
                self.Print_OrderBook()
            if (UserInput_Choice == 4):
                print(self.Current_Client_Public_Key)
            if (UserInput_Choice == 5):
                print(self.Current_Client_Private_Key)
            if (UserInput_Choice == 6):
                self.ClearScreen()
                continue
            if (UserInput_Choice == 7):
                break
            if (UserInput_Choice == 8):
                exit()
            #EndIf

            self.Pause()
        #EndWhile
    #EndFunction

    def Handle_Operation_Sell(self):
        self.Send_Data_to_Market(self.Get_Signed_Request_Message_for_Market())
    #EndFunction

    def Handle_Operation_Buy(self):
        self.Send_Data_to_Market(self.Get_Signed_Buy_Request_Message_for_Market())
    #EndFunction

    #
    def Handle_Incoming_BlockChain_from_Miner_THREADED(self):
        while True:
            BlockChain_Data_RAW, Miner_Address = self.Get_Data_from_Miner()
            if (len(BlockChain_Data_RAW)):
                #print("Received BlockChain {}".format(BlockChain_Data_RAW))
                Updated_BlockChain = json.loads(json.dumps(BlockChain_Data_RAW))
                print("Received BlockChain:")
                self.Print_JSON_Object(Updated_BlockChain)
                self.Update_Current_BlockChain(Updated_BlockChain)
            #EndIf
        #EndWhile
    #EndFunction
    # ----------------------------- HANDLERS -----------------------------

    # ----------------------------- MISC -----------------------------
    #OK
    def Get_BlockChain_Size(self):
        return len(self.BlockChain)
    #EndFunction

    #OK
    def Print_OrderBook(self):

        if (len(self.OrderBook) == 0):
            print("The order book is empty!")
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

    def Print_JSON_Object(self, target_object):
        print('\n', end='')

        print(json.dumps(target_object, indent=4, sort_keys=True))
        
        print('\n', end='')
    #EndFunction

    #OK
    def Print_BlockChain(self):
        self.Print_JSON_Object(self.BlockChain)
        print("BlockChain Size: {}".format(self.Get_BlockChain_Size()))
    #EndFunction
    # ----------------------------- MISC -----------------------------
    #
    def Get_Hashed_Username(self, target_username):
        return hashFunction.getSHA(target_username, 5)
    #EndFunction

    #Re-Written!
    def Get_Valid_Username_from_User(self):
        final_username = ""                 #Valid Username
        valid_username_found = True         #Found Flag

        #Open User DataBase File
        UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "r")

        #Keep inputting from user until valid username is obtained
        while True:

            #Get Username from user
            final_username = str(input("Enter Your Name Here: "))

            #Get Hash of the target Username
            target_hashed_username = self.Get_Hashed_Username(final_username)

            #Iterate through database to check if username already exists
            for current_line in UserDataBaseFile:
                current_user_entry_JSON = json.loads(current_line)
                if current_user_entry_JSON["hashed_username"] == target_hashed_username:
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
                print("[ERROR]: Can't use this Username! - \nAlready exists (Public key clash)\nPlease Choose another Username\n")
            #EndIf
        #EndWhile

        #Close The File
        UserDataBaseFile.close()

        #Return the valid Username
        return final_username
    #EndFunction

    #Re-Written!
    def Get_Valid_UserType_from_User(self):
        input_usertype = str(input("Write 'B' for buyer, 'S' for seller :"))
        
        while (input_usertype != "B" and input_usertype != "S"):
            print("Error write only 'B' or 'S'")
            input_usertype = str(input("Write 'B' for buyer, 'S' for seller :"))
        #EndWhile

        #Return UserType
        return input_usertype
    #EndFunction

    def Generate_User_RSA_Keys(self):
        self.Current_Client_Public_Key, self.Current_Client_Private_Key, self.Current_Client_RSA_KEY_OBJ = hashFunction.rsa_genkey()
        self.Current_Client_Public_Key_PEM = self.Current_Client_RSA_KEY_OBJ.public_key()
    #EndFunction

    def Update_UserDataBase_File(self):
        # Store into json file
        UserDataBaseFile = open(Client.USERDATABASE_FILE_NAME, "a")

        Database_Entry = {
            Client.MERCHANT_USERNAME_STR : self.Current_Client_Username,
            Client.Current_Client_HashedUsername : self.Current_Client_HashedUsername,
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

        print("User Succesfully registered")
    #EndFunction

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

    def Handle_New_User(self):
        #Get Current User name
        self.Current_Client_Username = self.Get_Valid_Username_from_User()
        
        #Get Current User type
        self.Current_Client_Type = self.Get_Valid_UserType_from_User()

        #Generate User's Public & Private Key
        self.Generate_User_RSA_Keys()
        
        #Save all current Client details into UserDataBase
        self.Update_UserDataBase_File()
    #EndFunction

    def Get_Signed_Request_Message_for_Market(self):
        Final_Signed_Market_Request_Message = ""

        UserInput_Item_Name = str(input("Enter Your Item name Here: "))
        UserInput_Item_Price = str(input("Enter Price For the Item Here: "))

        Market_Request_Message_String = "[{\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\"}" % (
            Client.MERCHANT_COMODITY_STR,
            UserInput_Item_Name,
            Client.MERCHANT_PRICE_STR,
            UserInput_Item_Price,
            Client.MERCHANT_PUBLIC_KEY_STR,
            self.Current_Client_Public_Key,
            Client.MERCHANT_TYPE_STR,
            self.Current_Client_Type
        )

        Market_Request_Digital_Signature = "{\"%s\":\"%s\"}]" % (
            Client.MERCHANT_SIGNATURE_STR,
            str((self.Get_Digital_Signature_using_PrivateKey(Market_Request_Message_String)).decode(Client.DATA_ENCODING_FORMAT))
        )

        Final_Signed_Market_Request_Message = Market_Request_Message_String + "," + Market_Request_Digital_Signature

        return Final_Signed_Market_Request_Message
    #EndFunction

    #Main Loop
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
    market_port = 2600
    miner_ip = market_ip
    miner_port = 2500
    client = Client(market_ip, market_port, miner_ip, miner_port)
    
    #Threading For BlockChain Update
    Client_BlockChain_Update_THREAD = Thread(target=client.Handle_Incoming_BlockChain_from_Miner_THREADED)
    Client_BlockChain_Update_THREAD.daemon = True
    Client_BlockChain_Update_THREAD.start()

    #Run The Client
    client.RunClient()
# EndMain

if __name__ == "__main__":
    main()
# EndIf