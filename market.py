# Market Code Here
import socket
import json

class Market:
    def __init__(self, server_ip, server_port, client_ip, client_port):

        # Socket Handling As Server For client.py
        self.ServerForClient_Socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind((server_ip, server_port))

        # Socket Handling As Client For miner.py
        self.ClientForMiner_Socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMiner_Socket.bind((client_ip, client_port))

        # Market Variables here
        self.OrderBook = []  # has dictionaries at each index

        self.TEST_BLOCK_CHAIN_TESTING_ONLY = '{"1":{"PreviousHash":"0x000000000000","Data":"0,1,100","Nonce":"852946123"},"2":{"PreviousHash":"0x000000000000","Data":"0,2,100","Nonce":"852946123"},"3":{"PreviousHash":"0x000000000000","Data":"0,3,100","Nonce":"852946123"},"4":{"PreviousHash":"0x000000000000","Data":"0,4,100","Nonce":"852946123"},"5":{"PreviousHash":"0x004433221100","Data":"1,2,12","Nonce":"681861688"},"6":{"PreviousHash":"0x006861831815","Data":"2,3,9","Nonce":"616840233"},"7":{"PreviousHash":"0x006516138131","Data":"3,4,8","Nonce":"694206900"},"8":{"PreviousHash":"0x006516138131","Data":"4,1,8","Nonce":"694206900"},"9":{"PreviousHash":"0x006516138131","Data":"2,4,5","Nonce":"694206900"}}'
        self.BlockChain = []

        #Testing ONLY
        self.BlockChain = json.loads(self.TEST_BLOCK_CHAIN_TESTING_ONLY)
        # self.

        #Stores list of Merchant Pkey, network Address that we have encountered
        self.ExistingMerchantList = []
    # EndFunction

    #OK
    def Add_To_OrderBook(self, merchant_type, merchant_public_key, comodity_to_sell, comodity_price):   

        self.OrderBook.append(
            {
                "m_type": merchant_type,
                "m_pkey": merchant_public_key,
                "m_item": comodity_to_sell,
                "m_price": comodity_price
            }
        )
    # EndFunction

    #OK
    def Get_Index_of_merchant_in_OrderBook(self, target_merchant_public_key):

        index = 0
        for current_merchant in self.OrderBook:

            if (current_merchant["m_pkey"] == target_merchant_public_key):
                return index
            #EndIf

            index += 1
        #EndFor

        #Return -1 to indicate we couldnt find the merchant
        return -1
    #EndFunction

    #OK
    def Remove_From_OrderBook(self, merchant_public_key):

        index = self.Get_Index_of_merchant_in_OrderBook(merchant_public_key)

        if (index != -1):
            self.OrderBook.pop(index)
        else:
            print("MERCHANT NOT FOUND. THIS SHOULDNT HAVE HAPPENED!")
        #EndIf
    # EndFunction

    #OK
    # Checks OrderBook for potential Transactions
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
                if (external_order_iterator["m_item"] == self.OrderBook[internal_order_iterator]["m_item"]):

                    #If External Iterator is Buyer
                    if (external_order_iterator["m_type"] == "Buyer"):

                        #If Internal Iterator is a Buyer
                        if (self.OrderBook[internal_order_iterator]["m_type"] == "Buyer"):

                            #Do nothing, its just a buyer vs buyer
                            pass

                        #If Internal Iterator is a Seller
                        elif (self.OrderBook[internal_order_iterator]["m_type"] == "Seller"):

                            #TXN if Buyer Price >= Seller
                            if (external_order_iterator["m_price"] >= self.OrderBook[internal_order_iterator]["m_price"]):
                                potential_TXNs.append((external_order_iterator["m_pkey"], self.OrderBook[internal_order_iterator]["m_pkey"]))
                            #EndIf
                        #EndIf

                    #If External Iterator is Seller
                    elif (external_order_iterator["m_type"] == "Seller"):

                        #If Internal Iterator is a Buyer
                        if (self.OrderBook[internal_order_iterator]["m_type"] == "Buyer"):

                            #TXN if Buyer Price >= Seller
                            if (self.OrderBook[internal_order_iterator]["m_price"] >= external_order_iterator["m_price"]):
                                potential_TXNs.append((external_order_iterator["m_pkey"], self.OrderBook[internal_order_iterator]["m_pkey"]))
                            #EndIf
                        
                        #If Internal Iterator is a Seller
                        elif (self.OrderBook[internal_order_iterator]["m_type"] == "Seller"):

                            #Do nothing, its just a Seller vs Seller
                            pass
                        #EndIf
                    #EndIf
                #EndIf
            #EndFor
        #EndFor

        print(potential_TXNs)
    # EndFunction

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

    #Send OrderBook to the Merchant requesting it
    def Send_OrderBook_to_Merchant(self, merchant_public_key):
        pass
    #EndFunction
    
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

    def Add_Merchant_to_Existing_List(self, merchant_public_key, merchant_network_addr):

        self.ExistingMerchantList.append(
            {
                "m_pkey" : merchant_public_key,
                "m_nAddr" : merchant_network_addr
            }
        )
    #EndFunction

    def Check_if_Merchant_Exists_in_Existing_List(self, merchant_public_key):

        for current_merchant in self.ExistingMerchantList:

            if (current_merchant["m_pkey"] == merchant_public_key):

                #Merchant found
                return True
            #EndIf
        #EndFor

        #Did not find merchant in list
        return False
    #EndFunction

    def RunMarket(self):

        #Main loop
        while True:
            pass
        #EndWhile
    #EndFunction
    
    def Get_BlockChain_Size(self):
        return len(self.BlockChain)
    #EndFunction

    #OK
    def Print_OrderBook(self):

        if (len(self.OrderBook) == 0):
            print("The order book is empty")
            return
        # EndIf

        index = 1
        for current_order in self.OrderBook:
            print("\nMerchant {}".format(index))
            print("Merchant Type : {}".format(current_order["m_type"]))
            print("Merchant Key  : {}".format(current_order["m_pkey"]))
            print("Merchant Item : {}".format(current_order["m_item"]))
            print("Merchant Price: {}".format(current_order["m_price"]))

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
        print("BlockChain Size: {}".format(len(self.BlockChain)))
    #EndFunction
# EndClass


def main():
    ip = "localhost"
    server_port = 2600
    client_port = 2500
    market = Market(ip, server_port, ip, client_port)
    market.Add_To_OrderBook("Buyer", 1, "Chair", 50)
    market.Add_To_OrderBook("Seller", 2, "Chair", 40)
    market.Add_To_OrderBook("Buyer", 3, "Fan", 30)
    market.Add_To_OrderBook("Seller", 4, "Fan", 40)
    #market.Print_OrderBook()
    #market.Remove_From_OrderBook(4)
    #print("\n---------------------------")
    #market.Get_All_Potential_TXN_in_OrderBook()
    #print("P Key: {}".format(market.Get_Index_of_merchant_in_OrderBook(1)))
    #print(market.Extract_Data_from_BlockChain_BlockData("56841536845368435684359865,958451856958698546982,500"))
    market.Print_BlockChain()
    print(market.Get_Merchant_Current_Balance("1"))
# EndMain


if __name__ == "__main__":
    main()
# EndIf