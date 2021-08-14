import socket
import json
import time
import hashFunction
import random
from threading import Thread
from ast import literal_eval
from os import system
import constants
import base64

class Client:

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

        print("Your Transaction History:")
        
        #Iterate thru entire chain for balance given to merchant
        for current_block_iterator in range(1, (self.Get_BlockChain_Size() + 1)):

            #Get Current Block as JSON obj
            current_block = self.BlockChain[str(current_block_iterator)]

            #Extract Data out of current block
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block[constants.MINER_BLOCKCHAIN_DATA_STR])

            #If Merchant Recieved Funds
            if (receiver_key == merchant_public_key):
                print("\nYou received {} from {}".format(amount_transfered, sender_key))
                balance_given_to_merchant += int(amount_transfered)
            #EndIf
        #EndFor

        #Iterate thru entire chain for balance taken from merchant
        for current_block_iterator in range(1, (self.Get_BlockChain_Size() + 1)):

            #Get Current Block as JSON obj
            current_block = self.BlockChain[str(current_block_iterator)]

            #Extract Data out of current block
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block[constants.MINER_BLOCKCHAIN_DATA_STR])

            #If Merchant Sent Funds
            if (sender_key == merchant_public_key):
                print("\nYou Sent {} to {}".format(sender_key, amount_transfered, receiver_key))
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
            incomming_UDP_Data = self.ClientForMarket_Socket.recvfrom(constants.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(constants.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            #print("\nException During Market Data Read: {}\n".format(e))
            return ("", "")
        #EndTry
    #EndFunction
    
    #Receives Data from Miner
    def Get_Data_from_Miner(self):
        try:
            incomming_UDP_Data = self.ClientForMiner_Socket.recvfrom(constants.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(constants.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            return ("", "")
        #EndTry
    #EndFunction

# --------------------------------- SOCKET SEND
    
    #Encodes Data and sends to Market
    def Send_Data_to_Market(self, data_to_send):
        self.ClientForMarket_Socket.sendto(
            str(data_to_send).encode(constants.DATA_ENCODING_FORMAT),
            self.ClientForMarket_SocketAddr
        )
    #EndFunction

    #Encodes Data and sends to Miner
    def Send_Data_to_Miner(self, data_to_send):
        self.ClientForMiner_Socket.sendto(
            data_to_send.encode(constants.DATA_ENCODING_FORMAT), 
            self.ClientForMiner_SocketAddr
        )
    #EndFunction

# --------------------------------- UPDATERS
    
    def Get_Latest_OrderBook_from_Market(self):

        #Open File
        OrderBook_File = open(constants.MARKET_ORDERBOOK_FILE_NAME, "r")
        #Read OrderBook
        New_OrderBook_RAW = OrderBook_File.read()
        #Close File
        OrderBook_File.close()

        #OrderBook is Empty 
        if (len(New_OrderBook_RAW) == 0):
            #Update Current OrderBook
            self.Update_Current_OrderBook(list())
            return
        #EndIf

        #Parse the current OrderBook
        New_OrderBook = literal_eval(New_OrderBook_RAW)

        #Update Current OrderBook
        self.Update_Current_OrderBook(New_OrderBook)
    #EndFunction

    #
    def Update_Current_OrderBook(self, new_orderbook):
        self.OrderBook = list(new_orderbook)
    #EndFunction    

    #
    def Update_Current_BlockChain(self, new_block_chain):
        self.BlockChain = dict(new_block_chain)
    #EndFunction

# --------------------------------- REQUESTS

    #Requests miner to send latest BlockChain
    #This function is used in threading for constant update of BlockChain
    def Request_Latest_BlockChain_from_Miner(self):
        self.Send_Data_to_Miner(constants.MINER_BLOCKCHAIN_REQUEST_STR)
    #EndFunction

    def Request_Initial_Funds_from_Market(self):
        Request_String = constants.MARKET_NEW_MERCHANT_REQUEST_STR
        Request_String += ":"

        #Form Msg Dict
        Msg_Dict = {
            constants.MERCHANT_PUBLIC_KEY_STR : self.Current_Client_Public_Key      #Send current Public Key
        }

        #Get Signed Dict
        Signed_Request_Dict = self.Generate_Signature_for_Message(Msg_Dict)

        #Stringify the final dict
        Request_String += str(Signed_Request_Dict)

        #Send the request to market
        self.Send_Data_to_Market(Request_String)
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

        #Request Market to assign us Initial Funds
        self.Request_Initial_Funds_from_Market()

        self.Console_Delay(1)
    #EndFunction

    #Place bid on the Market
    def Handle_Market_Buy_Sell_Operation(self):
        self.Send_Data_to_Market(self.Get_Signed_Market_Buy_Sell_Request_String())
    #EndFunction

    #Main Menu Handler
    def Handle_Main_Menu(self):
        while True:

            #Request Miner To Send Latest BlockChain
            #Received BlockChain asynchronously updated using threads
            self.Request_Latest_BlockChain_from_Miner()

            self.Console_ClearScreen()

            print("User: {}".format(self.Current_Client_Username))
            print("Type: {}\n".format(self.Current_Client_Type))

            # Menu 
            print("       Main Menu\n")


            print("1. View Current balance")
            if (self.Current_Client_Type == constants.MERCHANT_TYPE_SELLER_STR):
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
                self.Console_Delay(1)
                self.Console_ClearScreen()
                continue
            #EndTry

            #View Current balance
            if (UserInput_Choice == 1):

                #Request Miner To Send Latest BlockChain
                #Received BlockChain asynchronously updated using threads
                self.Request_Latest_BlockChain_from_Miner()

                print("\nYour Current Balance is: {}".format(self.Get_Merchant_Current_Balance(self.Current_Client_Public_Key)))

            #Buy/Sell Something
            if (UserInput_Choice == 2):

                self.Handle_Market_Buy_Sell_Operation()

                print("\nYour Request has been added to the OrderBook!")
            
            #View Orderbook
            if (UserInput_Choice == 3):

                self.Get_Latest_OrderBook_from_Market()
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
            #print("\nAttempting Data Read From Miner..")
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

    # def Handle_Incoming_OrderBook_from_Market_THREADED(self):
    #     while True:
    #         print("\nAttempting Data Read From Market..")
    #         OrderBook_Data_RAW, Market_Addr = self.Get_Data_from_Market()

    #         if (len(OrderBook_Data_RAW)):
    #             print("Received: '{}' from 'localhost:{}'".format(OrderBook_Data_RAW, Market_Addr[1]))

    #             Updated_OrderBook = literal_eval(OrderBook_Data_RAW)

    #             self.Update_Current_OrderBook(Updated_OrderBook)

    #         #EndIf
    #     #EndWhile
    # #EndFunction

# --------------------------------- USER

    #Checks for duplicate PublicKey
    #Loops until unique PublicKey is obtained from Username
    #Checks the Json file for Data regarding keys
    def Get_Valid_Username_from_User(self):
        final_username = ""                 #Valid Username

        #Try to Open User DataBase File
        try:
            UserDataBaseFile = open(constants.USERDATABASE_FILE_NAME, "r")
        except (FileNotFoundError):
            #No File exists
            print("\n[INFO]: UserDataBase file '{}' doesnt exist!\nMaking a new one...\n".format(constants.USERDATABASE_FILE_NAME))

            #Create the file
            NEW_UserDataBaseFile = open(constants.USERDATABASE_FILE_NAME, "w")
            #Close it immediately because we dont want to write any data to it
            NEW_UserDataBaseFile.close()

            #Try opening the file again
            try:
                UserDataBaseFile = open(constants.USERDATABASE_FILE_NAME, "r")
            except Exception as e:
                #This shouldnt have happened
                print("\n[ERROR]: {} Attempted to create UserDataBase file '{}' failed!!\nExact Error: {}\nExiting\n".format(constants.USERDATABASE_FILE_NAME, e))
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
                if current_user_entry_JSON[constants.MERCHANT_HASHED_USERNAME_STR] == target_hashed_username:
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

        #Get Uppercase
        input_usertype = input_usertype.upper()
        
        while (input_usertype != "B" and input_usertype != "S"):
            print("\n[ERROR]: Enter 'B' or 'S' only!")
            input_usertype = str(input("\nEnter 'B' if you're a Buyer or 'S' if a Seller: "))
        #EndWhile

        #Return UserType
        if (input_usertype == "B"):
            return constants.MERCHANT_TYPE_BUYER_STR
        else:
            return constants.MERCHANT_TYPE_SELLER_STR
        #EndIf
    #EndFunction

    #Generate Current User's RSA Keys
    def Generate_User_RSA_Keys(self):
        self.Current_Client_Public_Key, self.Current_Client_Private_Key, self.Current_Client_RSA_KEY_OBJ = hashFunction.rsa_genkey()
        self.Current_Client_Public_Key_PEM = self.Current_Client_RSA_KEY_OBJ.public_key()
    #EndFunction

    #Write Userinfo onto the UserDataBase JSON file
    def Update_UserDataBase_File(self):
        # Store into json file
        UserDataBaseFile = open(constants.USERDATABASE_FILE_NAME, "a")

        Database_Entry = {
            constants.MERCHANT_USERNAME_STR : self.Current_Client_Username,
            constants.MERCHANT_HASHED_USERNAME_STR : self.Current_Client_HashedUsername,
            constants.MERCHANT_PUBLIC_KEY_STR : self.Current_Client_Public_Key,
            constants.MERCHANT_PRIVATE_KEY_STR : self.Current_Client_Private_Key,
            constants.MERCHANT_TYPE_STR : self.Current_Client_Type,
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
        return hashFunction.generate_signature(target_message, self.Current_Client_RSA_KEY_OBJ)
    #EndFunction

    def Verify_Digital_Signature_using_PublicKey(self, target_signature, target_message, target_public_key):
        if (hashFunction.verify_signature(target_signature, target_message, target_public_key)):
            print("Signature Verified from public key")
            return True
        else:
            print("Cannot Verify")
            return False
        #EndIf
    #EndFunction

    #Takes in target msg dictionary and returns a dictionary with
    # MSG : target_msg_dict
    # SIGN : Signature (Base64 Encoded as it was in bytes)
    def Generate_Signature_for_Message(self, target_msg_dict):

        #Convert target dict into string
        target_msg_str = str(target_msg_dict)

        #Generate the signature of stringified dict
        Signature_Bytes = self.Get_Digital_Signature_using_PrivateKey(target_msg_str)

        #Base64 Encode the signature obj (which was of type Bytes)
        Base64_Encoded_Signature = base64.b64encode(Signature_Bytes)

        #Form final dict with msg and its sign (base64 encoded)
        Signed_Request_Msg_Dict = {
            constants.MERCHANT_SIGNATURE_MSG_STR : target_msg_dict,
            constants.MERCHANT_SIGNATURE_SIGN_STR : Base64_Encoded_Signature.decode(constants.MERCHANT_SIGNATURE_ENCODING_STR)
        }

        #Return Final Dict
        return Signed_Request_Msg_Dict
    #EndFunction

    def Get_Signed_Market_Buy_Sell_Request_String(self):

        #Returns String in Format:
        #  ODR:{"Msg":{MARKET_REQUEST_DICT},"Sign":{BASE_64_ENCODED_SIGNATURE}}

        Final_Signed_Market_Request_Msg_String = constants.MARKET_NEW_ORDER_REQUEST_STR
        Final_Signed_Market_Request_Msg_String += ":"

        UserInput_Item_Name = str(input("\nEnter Your Item name Here: "))
        UserInput_Item_Price = str(input("Enter Price For the Item Here: "))

        #
        Market_Request_Dict = {
            constants.MERCHANT_PUBLIC_KEY_STR : self.Current_Client_Public_Key,
            constants.MERCHANT_TYPE_STR : self.Current_Client_Type,
            constants.MERCHANT_COMODITY_STR : UserInput_Item_Name,
            constants.MERCHANT_PRICE_STR : UserInput_Item_Price
        }

        Signed_Request_Dict = self.Generate_Signature_for_Message(Market_Request_Dict)

        Final_Signed_Market_Request_Msg_String += str(Signed_Request_Dict)

        # Market_Request_String = "{\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\",\"%s\":\"%s\"}" % (
        #     constants.MERCHANT_COMODITY_STR,
        #     UserInput_Item_Name,
        #     constants.MERCHANT_PRICE_STR,
        #     UserInput_Item_Price,
        #     constants.MERCHANT_PUBLIC_KEY_STR,
        #     self.Current_Client_Public_Key,
        #     constants.MERCHANT_TYPE_STR,
        #     self.Current_Client_Type
        # )

        # Market_Request_String = str(Market_Request_Dict)

        # #
        # Signature_Bytes = self.Get_Digital_Signature_using_PrivateKey(Market_Request_String)

        # Base64_Encoded_Signature = base64.b64encode(Signature_Bytes)

        # Signed_Market_Request_Msg_Dict = {
        #     constants.MERCHANT_SIGNATURE_MSG_STR : Market_Request_Dict,
        #     constants.MERCHANT_SIGNATURE_SIGN_STR : Base64_Encoded_Signature.decode(constants.MERCHANT_SIGNATURE_ENCODING_STR)
        # }

        # Final_Signed_Market_Request_Msg_String += str(Signed_Market_Request_Msg_Dict)

        return Final_Signed_Market_Request_Msg_String
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

        #New Line
        print("")
        print("OrderBook:\n")

        print(' | {0:^10} | {1:^10} | {2:^10} | {3:^10} |'.format('Key','Type','Item', 'Price'))

        for current_order in self.OrderBook:

            print(' | {0:^10} | {1:^10} | {2:^10} | {3:^10} |'.format(
                ".." + current_order[constants.MERCHANT_PUBLIC_KEY_STR][-7:],   #Print Last 7 charecters of Public Key
                current_order[constants.MERCHANT_TYPE_STR],
                current_order[constants.MERCHANT_COMODITY_STR], 
                current_order[constants.MERCHANT_PRICE_STR]
                )
            )
            
            #print("\nMerchant {}".format(index))
            # print("Merchant Key  : {}".format(current_order[constants.MERCHANT_PUBLIC_KEY_STR]))
            # print("Merchant Type : {}".format(current_order[constants.MERCHANT_TYPE_STR]))
            # print("Merchant Item : {}".format(current_order[constants.MERCHANT_COMODITY_STR]))
            # print("Merchant Price: {}".format(current_order[constants.MERCHANT_PRICE_STR]))

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

    #Client Object
    client = Client(market_ip, client_for_market_port, miner_ip, client_for_miner_port)
    
    #Threading For BlockChain Update
    Client_BlockChain_Update_THREAD = Thread(target=client.Handle_Incoming_BlockChain_from_Miner_THREADED)
    Client_BlockChain_Update_THREAD.daemon = True
    Client_BlockChain_Update_THREAD.start()

    #Run The Client
    client.RunClient()
#EndMain

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nExiting Client\nGoodBye!\n")
        exit()
    #EndTry
#EndIf