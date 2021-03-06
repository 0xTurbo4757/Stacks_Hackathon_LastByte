# Market Code Here
import socket
import json
from ast import literal_eval
from threading import Thread
import constants
import base64
import hashFunction

class Market:

# --------------------------------- CONSTRUCTOR

    def __init__(self, server_ip, server_port, client_ip, client_port):

        # Socket Handling As Server For client.py
        self.ServerForClient_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind((server_ip, server_port))
        self.ServerForClient_Socket.settimeout(1.0)

        # Socket Handling As Client For miner.py
        self.ClientForMiner_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMiner_Socket.connect((client_ip, client_port))
        self.ClientForMiner_SocketAddr = (client_ip, client_port)

        # Market Variables here
        self.OrderBook = []  # has dictionaries at each index

        self.TEST_BLOCK_CHAIN_TESTING_ONLY = '{"1":{"PreviousHash":"0x000000000000","Data":"0,1,100","Nonce":"852946123"},"2":{"PreviousHash":"0x000000000000","Data":"0,2,100","Nonce":"852946123"},"3":{"PreviousHash":"0x000000000000","Data":"0,3,100","Nonce":"852946123"},"4":{"PreviousHash":"0x000000000000","Data":"0,4,100","Nonce":"852946123"},"5":{"PreviousHash":"0x004433221100","Data":"1,2,12","Nonce":"681861688"},"6":{"PreviousHash":"0x006861831815","Data":"2,3,9","Nonce":"616840233"},"7":{"PreviousHash":"0x006516138131","Data":"3,4,8","Nonce":"694206900"},"8":{"PreviousHash":"0x006516138131","Data":"4,1,8","Nonce":"694206900"},"9":{"PreviousHash":"0x006516138131","Data":"2,4,5","Nonce":"694206900"}}'
        
        # Entire BlockChain as dictionary
        self.BlockChain = {}

        #Testing ONLY
        #self.BlockChain = json.loads(self.TEST_BLOCK_CHAIN_TESTING_ONLY)
        # self.

        #Stores list of Merchant Pkey, network Address that we have encountered
        self.ExistingMerchantList = []
    # EndFunction

# --------------------------------- MERCHANT
    
    def Add_Merchant_To_OrderBook(self, merchant_type, merchant_public_key, comodity_to_sell, comodity_price):   

        self.OrderBook.append(
            {
                constants.MERCHANT_TYPE_STR: merchant_type,
                constants.MERCHANT_PUBLIC_KEY_STR : merchant_public_key,
                constants.MERCHANT_COMODITY_STR: comodity_to_sell,
                constants.MERCHANT_PRICE_STR: comodity_price
            }
        )
    # EndFunction

    def Get_Index_of_merchant_in_OrderBook(self, merchant_public_key):

        index = 0
        for current_merchant in self.OrderBook:

            if (current_merchant[constants.MERCHANT_PUBLIC_KEY_STR] == merchant_public_key):
                return index
            #EndIf

            index += 1
        #EndFor

        #Return -1 to indicate we couldnt find the merchant
        return -1
    #EndFunction

    def Check_if_Merchant_Exists_in_OrderBook(self, merchant_public_key):
        for current_merchant in self.OrderBook:
            if (current_merchant[constants.MERCHANT_PUBLIC_KEY_STR] == merchant_public_key):
                return True
            #EndIf
        #EndFor

        #Return False to indicate we couldnt find the merchant
        return False
    #EndFunction

    #Returns Merchant Data as Dictionary
    def Get_Merchant_Data_from_OrderBook(self, target_merchant_public_key):
        for current_merchant in self.OrderBook:

            if (current_merchant[constants.MERCHANT_PUBLIC_KEY_STR] == target_merchant_public_key):
                return current_merchant
            #EndIf
        #EndFor

        #Return a None to tell data not found
        return None
    #EndFunction

    def Remove_Merchant_From_OrderBook(self, merchant_public_key):

        index = self.Get_Index_of_merchant_in_OrderBook(merchant_public_key)

        if (index != -1):
            self.OrderBook.pop(index)
        else:
            print("MERCHANT NOT FOUND. THIS SHOULDNT HAVE HAPPENED!")
        #EndIf
    #EndFunction

    def Add_Merchant_to_ExistingMerchants_List(self, merchant_public_key, merchant_network_addr):

        self.ExistingMerchantList.append(
            {
                constants.MERCHANT_PUBLIC_KEY_STR : merchant_public_key,
                constants.MERCHANT_IP_STR : merchant_network_addr[0],
                constants.MERCHANT_PORT_STR : merchant_network_addr[1]
            }
        )
    #EndFunction

    def Get_Merchant_Data_from_ExistingMerchants_List(self, merchant_public_key):
        for current_merchant in self.ExistingMerchantList:

            if (current_merchant[constants.MERCHANT_PUBLIC_KEY_STR] == merchant_public_key):
                return current_merchant
            #EndIf
        #EndFor

        #Return a None to tell data not found
        return None
    #EndFunction

    def Check_if_Merchant_Exists_in_ExistingMerchant_List(self, merchant_public_key):

        for current_merchant in self.ExistingMerchantList:

            if (current_merchant[constants.MERCHANT_PUBLIC_KEY_STR] == merchant_public_key):

                #Merchant found
                return True
            #EndIf
        #EndFor

        #Did not find merchant in list
        return False
    #EndFunction

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
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block[constants.MINER_BLOCKCHAIN_DATA_STR])

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
            sender_key,receiver_key,amount_transfered = self.Extract_Data_from_BlockChain_BlockData(current_block[constants.MINER_BLOCKCHAIN_DATA_STR])

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
    #EndFunction
    
    #Returns True or False
    def Verify_Merchant_has_Enough_Balance(self, merchant_public_key):
        return (self.Get_Merchant_Current_Balance(merchant_public_key) >= 0)
    #EndFunction

    # Checks OrderBook for potential Transactions
    # Returns a list of tuples of TXN pKeys: buyer,seller
    def Get_All_Potential_TXN_in_OrderBook(self):
        
        #Stores Tuple of Buyer,Seller Public Keys who can Transact
        potential_TXNs = []

        #Return if none or just 1 order in orderBook
        if ((len(self.OrderBook) == 0) or (len(self.OrderBook) == 1)):
            return
        #EndIf

        #Get All Potential Transactions in the order book
        #For Each order in OrderBook
        for external_order_iterator in self.OrderBook:

            #For Each order in OrderBook starting from 2nd Element
            for internal_order_iterator in range(1, len(self.OrderBook)):

                #If current Order type matches the other order type in the order list
                if (external_order_iterator[constants.MERCHANT_COMODITY_STR] == self.OrderBook[internal_order_iterator][constants.MERCHANT_COMODITY_STR]):

                    #If External Iterator is Buyer
                    if (external_order_iterator[constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_BUYER_STR):

                        #If Internal Iterator is a Buyer
                        if (self.OrderBook[internal_order_iterator][constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_BUYER_STR):

                            #Do nothing, its just a buyer vs buyer
                            pass

                        #If Internal Iterator is a Seller
                        elif (self.OrderBook[internal_order_iterator][constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_SELLER_STR):

                            #TXN if Buyer Price >= Seller
                            if (external_order_iterator[constants.MERCHANT_PRICE_STR] >= self.OrderBook[internal_order_iterator][constants.MERCHANT_PRICE_STR]):
                                potential_TXNs.append((external_order_iterator[constants.MERCHANT_PUBLIC_KEY_STR], self.OrderBook[internal_order_iterator][constants.MERCHANT_PUBLIC_KEY_STR]))
                            #EndIf
                        #EndIf

                    #If External Iterator is Seller
                    elif (external_order_iterator[constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_SELLER_STR):

                        #If Internal Iterator is a Buyer
                        if (self.OrderBook[internal_order_iterator][constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_BUYER_STR):

                            #TXN if Buyer Price >= Seller
                            if (self.OrderBook[internal_order_iterator][constants.MERCHANT_PRICE_STR] >= external_order_iterator[constants.MERCHANT_PRICE_STR]):
                                potential_TXNs.append((self.OrderBook[internal_order_iterator][constants.MERCHANT_PUBLIC_KEY_STR], external_order_iterator[constants.MERCHANT_PUBLIC_KEY_STR]))
                            #EndIf
                        
                        #If Internal Iterator is a Seller
                        elif (self.OrderBook[internal_order_iterator][constants.MERCHANT_TYPE_STR] == constants.MERCHANT_TYPE_SELLER_STR):

                            #Do nothing, its just a Seller vs Seller
                            pass
                        #EndIf
                    #EndIf
                #EndIf
            #EndFor
        #EndFor

        print("Potential TXN: \n{}\n".format(potential_TXNs))

        #Return all possible TXNs
        return potential_TXNs
    # EndFunction    

# --------------------------------- SOCKET RECEIVE

    def Get_Data_from_Merchant(self):
        try:
            incomming_UDP_Data = self.ServerForClient_Socket.recvfrom(constants.UDP_DATA_BUFFER_SIZE)
            Data = incomming_UDP_Data[0].decode(constants.DATA_ENCODING_FORMAT)
            return ((Data, incomming_UDP_Data[1]))
        except:
            return ("", "")
        #EndTry
    #EndFunction

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

    def Send_Data_to_Merchant(self, data_to_send, merchant_addr):
        self.ServerForClient_Socket.sendto(
            str(data_to_send).encode(constants.DATA_ENCODING_FORMAT), 
            merchant_addr
        )
    #EndFunction

    def Send_Data_to_Miner(self, data_to_send):
        self.ClientForMiner_Socket.sendto(
            str(data_to_send).encode(constants.DATA_ENCODING_FORMAT), 
            self.ClientForMiner_SocketAddr
        )
    #EndFunction

    #Send OrderBook to the Merchant requesting it using merchant Addr (tuple)
    def Send_OrderBook_to_Merchant(self, merchant_addr):
        self.Send_Data_to_Merchant(
            #OrderBook
            self.OrderBook,
            #Address Tuple
            merchant_addr
        )
    #EndFunction

    #Send OrderBook to the Merchant requesting it using Existing Merchant List
    def Send_OrderBook_to_Merchant(self, merchant_public_key):
        target_merchant = self.Get_Merchant_Data_from_ExistingMerchants_List(merchant_public_key)

        if (target_merchant == None):
            return
        #EndIf

        #Send OrderBook
        self.Send_OrderBook_to_Merchant((target_merchant[constants.MERCHANT_IP_STR], target_merchant[constants.MERCHANT_PORT_STR]))
    #EndFunction

# --------------------------------- UPDATERS

    def Update_Current_BlockChain(self, new_block_chain):
        self.BlockChain = dict(new_block_chain)
    #EndFunction

    #Update Orderbook to a file
    def Update_Orderbook_to_File(self):
        New_OrderBook = open("orderbook.txt","w")
        New_OrderBook.write(str(self.OrderBook))
        New_OrderBook.close()
    #EndFunction

# --------------------------------- REQUESTS

    #TXN Data tuple: (SENDER, RECEIVER, AMOUNT)
    def Request_Miner_to_Add_TXN_to_BlockChain(self, TXN_Data):
        #Generate Request for miner: "TXN:SENDER,RECEIVER,AMOUNT"
        request_to_send_miner = "TXN:"
        request_to_send_miner += str(TXN_Data[0])
        request_to_send_miner += ","
        request_to_send_miner += str(TXN_Data[1])
        request_to_send_miner += ","
        request_to_send_miner += str(TXN_Data[2])

        #Request MINER HERE : SOCKET
        print("\nRequested Miner '{}'".format(request_to_send_miner))
        self.Send_Data_to_Miner(request_to_send_miner)
    #EndFunction

    def Request_Latest_BlockChain_from_Miner(self):
        self.Send_Data_to_Miner(constants.MINER_BLOCKCHAIN_REQUEST_STR)
    #EndFunction

    def Request_Miner_to_give_New_Merchant_Funds(self, merchant_public_key):
        self.Request_Miner_to_Add_TXN_to_BlockChain(
            (
                constants.MINER_DEFAULT_ADDRESS,
                merchant_public_key,
                constants.NEW_MERCHANT_FUND_AMOUNT
            )
        )
    #EndFunction

# --------------------------------- DIGITAL SIGNATURE

    def Verify_Digital_Signature_using_PublicKey(self, target_signature, target_message, target_public_key):
        if (hashFunction.verify_signature(target_signature, target_message, target_public_key)):
            print("Signature Verified from public key")
            return True
        else:
            print("Cannot Verify")
            return False
        #EndIf
    #EndFunction

# --------------------------------- HANDLERS

    def Handle_All_Potential_TXNs_within_OrderBook(self):
        
        list_of_all_TXNs_possible = self.Get_All_Potential_TXN_in_OrderBook()

        #There are no TXNs to make
        if (list_of_all_TXNs_possible == None):
            return
        #EndIf

        #For All possible TXNs
        for current_TXN in self.Get_All_Potential_TXN_in_OrderBook():
            
            #If Buyer has enough Balance
            if (self.Verify_Merchant_has_Enough_Balance(current_TXN[0])):

                #Get Buyer Seller Data as Dict
                Buyer = self.Get_Merchant_Data_from_OrderBook(current_TXN[0])
                Seller = self.Get_Merchant_Data_from_OrderBook(current_TXN[1])

                #Error Handling
                if (Buyer == None or Seller == None):
                    #TXN cant Happen. Buyer Seller Not Found
                    print("TXN cant Happen. Buyer {} Seller {} Not Found".format(current_TXN[0], current_TXN[1]))
                    continue
                #EndIf

                #Calculate Transfer Ammount
                transfer_ammount = min(int(Buyer[constants.MERCHANT_PRICE_STR]), int(Seller[constants.MERCHANT_PRICE_STR]))

                #Request Miner to add TXN in BlockChain
                self.Request_Miner_to_Add_TXN_to_BlockChain(

                    #Send a tuple
                    (
                        #Sender Address (Buyer)
                        current_TXN[0],

                        #Receiver Address (Seller)
                        current_TXN[1],

                        #Amount Transfered (Min of what buyer was giving and seller was demanding)
                        transfer_ammount
                    )
                )

                #clear OrderBook of Buyer and Seller
                self.Remove_Merchant_From_OrderBook(current_TXN[0])      #Remove Buyer Entry in OrderBook
                self.Remove_Merchant_From_OrderBook(current_TXN[1])      #Remove Seller Entry in OrderBook

                #Write Latest OrderBook Data to File
                self.Update_Orderbook_to_File()

            else:
                #Tell Buyer here that ur TXN cannot continue, not enough funds
                pass
            #EndIf
        #EndFor
    #EndFunction

    def Handle_Incoming_Request_from_Merchant(self):

        print("\nListening for Client Request")
        Incoming_Data, Client_Address = self.Get_Data_from_Merchant()

        if (len(Incoming_Data)):
            print("\n\nReceived Data: {}".format(Incoming_Data))
            print("From Addr    : {}\n".format(Client_Address))

            #client Requested latest Orderbook
            if (Incoming_Data == constants.CLIENT_ORDERBOOK_REQUEST_STR):

                print("Sending OrderBook: \n{}\n\nto Client: {}".format(self.OrderBook, Client_Address))
                self.Send_OrderBook_to_Merchant(Client_Address)

            #client Requested initial funds from miner
            elif (Incoming_Data[0:3] == constants.MARKET_NEW_MERCHANT_REQUEST_STR):

                #The request is in format: NEW:PUB_KEY
                Initial_Funds_Signed_Request_Str = Incoming_Data[4:]

                #Parse Incoming Dict with sign
                try:
                    Initial_Funds_Signed_Request_Dict = dict(literal_eval(Initial_Funds_Signed_Request_Str))
                except Exception as e:
                    print("OrderBook Decoder couldnt Parse Request {}\nError: {}".format(Incoming_Data, e))
                    print("Request Ignored :(")
                    return
                #EndTry

                #Get Data out of Dict, Msg has Merchant Public Key
                Merchant_Public_Key = Initial_Funds_Signed_Request_Dict[constants.MERCHANT_SIGNATURE_MSG_STR][constants.MERCHANT_PUBLIC_KEY_STR]

                #if Merchant doesnt Exists in ListOfUniqueMerchants
                if (not(self.Check_if_Merchant_Exists_in_ExistingMerchant_List(Merchant_Public_Key))):

                    #Add Merchant to Existing Merchant List
                    self.Add_Merchant_to_ExistingMerchants_List(
                        Merchant_Public_Key,
                        Client_Address
                    )

                    #Request Miner to give new merchant funds
                    self.Request_Miner_to_give_New_Merchant_Funds(Merchant_Public_Key)
                #EndIf

            #client Requested to add bid into Orderbook
            elif (Incoming_Data[0:3] == constants.MARKET_NEW_ORDER_REQUEST_STR):

                #The request is in format: ODR:{MERCHANT_JSON_OBJ}
                OrderBook_Signed_Request_Str = Incoming_Data[4:]

                #Parse Incoming Dict with sign
                try:
                    OrderBook_Signed_Request_Dict = dict(literal_eval(OrderBook_Signed_Request_Str))
                except Exception as e:
                    print("OrderBook Decoder couldnt Parse Request {}\nError: {}".format(Incoming_Data, e))
                    print("Request Ignored :(")
                    return
                #EndTry

                #Get Dict out of incoming Dict
                Merchant_OrderBook_Add_JSON = OrderBook_Signed_Request_Dict[constants.MERCHANT_SIGNATURE_MSG_STR]

                #if Merchant doesnt Exists in OrderBook
                if (not(self.Check_if_Merchant_Exists_in_OrderBook(Merchant_OrderBook_Add_JSON[constants.MERCHANT_PUBLIC_KEY_STR]))):

                    #Add Merchant Request to OrderBook
                    self.Add_Merchant_To_OrderBook(
                        Merchant_OrderBook_Add_JSON[constants.MERCHANT_TYPE_STR],
                        Merchant_OrderBook_Add_JSON[constants.MERCHANT_PUBLIC_KEY_STR],
                        Merchant_OrderBook_Add_JSON[constants.MERCHANT_COMODITY_STR],
                        Merchant_OrderBook_Add_JSON[constants.MERCHANT_PRICE_STR]
                    )

                    #Write Latest OrderBook Data to File
                    self.Update_Orderbook_to_File()
                #EndIf
            #EndIf
        #EndIf
    #EndFunction

# --------------------------------- THREADED HANDLERS

    def Handle_Incoming_BlockChain_from_Miner_THREADED(self):
        while True:
            BlockChain_Data_RAW, Miner_Address = self.Get_Data_from_Miner()
            #print("\nReceived BlockChain, Type = {}\n".format(type(BlockChain_Data_RAW)))
            
            if (len(BlockChain_Data_RAW)):
                #print("Received BlockChain {}".format(BlockChain_Data_RAW))

                #Updated_BlockChain = json.loads(json.dumps(BlockChain_Data_RAW))
                Updated_BlockChain = literal_eval(BlockChain_Data_RAW)
                
                print("\nReceived BlockChain:")
                self.Print_JSON_Object(Updated_BlockChain)
                self.Update_Current_BlockChain(Updated_BlockChain)
            
            #EndIf
        #EndWhile
    #EndFunction

# --------------------------------- MISC

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

    def Get_BlockChain_Size(self):
        #print("BlockChain Blocks: {}".format(self.BlockChain.keys()))

        #len() on a dict returns number of top level keys in dict
        return len(self.BlockChain)
    #EndFunction

    def Print_OrderBook(self):

        if (len(self.OrderBook) == 0):
            print("The order book is empty")
            return
        # EndIf

        index = 1
        for current_order in self.OrderBook:
            print("\nMerchant {}".format(index))
            print("Merchant Type : {}".format(current_order[constants.MERCHANT_TYPE_STR]))
            print("Merchant Key  : {}".format(current_order[constants.MERCHANT_PUBLIC_KEY_STR]))
            print("Merchant Item : {}".format(current_order[constants.MERCHANT_COMODITY_STR]))
            print("Merchant Price: {}".format(current_order[constants.MERCHANT_PRICE_STR]))

            index += 1
        # EndFor
    #EndFunction

    def Print_JSON_Object(self, target_object):
        print('\n', end='')

        print(json.dumps(target_object, indent=4, sort_keys=True))
        
        print('\n', end='')
    #EndFunction

    def Print_BlockChain(self):
        self.Print_JSON_Object(self.BlockChain)
        print("BlockChain Size: {}".format(self.Get_BlockChain_Size()))
    #EndFunction

    def Reset_OrderBook_File(self):
        New_OrderBook = open("orderbook.txt","w")
        New_OrderBook.close()
    #EndFunction

# --------------------------------- RUN

    #Main Loop
    def RunMarket(self):

        #Main loop
        while True:

            #Handle Client.py requesting Latest OrderBook or Request To Add New Order
            #Also Adds New Unique merchant in ExistingMerchantList
            #If New Merchant, Requests Miner to give default fund to Merchant (Sends TXN request)
            self.Handle_Incoming_Request_from_Merchant()

            #Keeps Checking OrderBook for potential TXN
            #If TXN possible, Calculates Balance of Buyer
            #If Sufficient Balance exists, 
            #Sends TXN request to miner
            #Then Removes Buyer & Seller entry in OrderBook
            self.Handle_All_Potential_TXNs_within_OrderBook()

            #Request Miner To Send Latest BlockChain
            #Received BlockChain asynchronously updated using threads
            self.Request_Latest_BlockChain_from_Miner()

            #TESTING ONLY
            # self.Request_Miner_to_Add_TXN_to_BlockChain(
            #     (
            #         0,
            #         1,
            #         50
            #     )
            # )

        #EndWhile
    #EndFunction

#EndClass

def main():
    ip = "localhost"
    server_for_client_port = 56000
    client_for_miner_port = 55000

    #Miner Object
    market = Market(ip, server_for_client_port, ip, client_for_miner_port)
    
    #Threading For BlockChain Update
    Market_BlockChain_Update_THREAD = Thread(target=market.Handle_Incoming_BlockChain_from_Miner_THREADED)
    Market_BlockChain_Update_THREAD.daemon = True
    Market_BlockChain_Update_THREAD.start()

    #Reset The OrderBook File
    market.Reset_OrderBook_File()

    #Run The market
    market.RunMarket()
#EndMain

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nExiting Market\nGoodBye!\n")
        exit()
    #EndTry
#EndIf