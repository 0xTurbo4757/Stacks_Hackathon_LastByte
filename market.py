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

        self.BlockChain = []
        # self.
    # EndFunction

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
    def Remove_From_OrderBook(self, merchant_public_key):

        index = self.Get_Index_of_merchant_in_OrderBook(merchant_public_key)

        if (index != -1):
            self.OrderBook.pop(index)
        else:
            print("MERCHANT NOT FOUND. THIS SHOULDNT HAVE HAPPENED!")
        #EndIf
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

    # Iterates through Blockchain to get latest Balance
    def Get_Merchant_Current_Balance(self, merchant_public_key):
        pass
    # EndFunction

    def Run(self):

        # Main loop
        while True:
            pass
        # EndWhile
    # EndFunction
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
    market.Print_OrderBook()
    #market.Remove_From_OrderBook(4)
    print("\n---------------------------")

    market.Get_All_Potential_TXN_in_OrderBook()
    #print("P Key: {}".format(market.Get_Index_of_merchant_in_OrderBook(1)))
# EndMain


if __name__ == "__main__":
    main()
# EndIf
