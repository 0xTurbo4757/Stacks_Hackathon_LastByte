# Market Code Here
import socket

class Market:
    def __init__(self, server_ip, server_port, client_ip, client_port):

        #Socket Handling As Server For client.py
        self.ServerForClient_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind(server_ip, server_port)

        #Socket Handling As Client For miner.py
        self.ClientForMiner_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ClientForMiner_Socket.bind(client_ip, client_port)

        #Market Variables here
        self.OrderBook = [] #has dictionaries at each index
        #self.

    #EndFunction

    def Add_To_OrderBook(self, merchant_type, merchant_public_key, comodity_to_sell, comodity_price):
        
        self.OrderBook.append(
            {
                "m_type" : merchant_type,
                "m_pkey" : merchant_public_key,
                "m_item" : comodity_to_sell,
                "m_price" : comodity_price
            }
        )
    #EndFunction

    def Remove_From_OrderBook(self, merchant_type, merchant_public_key, comodity_to_sell, comodity_price):

        index = self.Get_Index_of_data_in_OrderBook(merchant_public_key)

        self.OrderBook.pop(index)
    #EndFunction

    def Get_Index_of_data_in_OrderBook(self, merchant_public_key):

    #EndFunction

    def Print_OrderBook(self):

        if (len(self.OrderBook) == 0):
            print("The order book is empty")
            return
        #EndIf

        for current_order in self.OrderBook:

            print("Merchant Type : {}".format(current_order["m_type"]))
            print("Merchant Key  : {}".format(current_order["m_pkey"]))
            print("Merchant Item : {}".format(current_order["m_type"]))
            print("Merchant Price: {}".format(current_order["m_type"]))
        #EndFor
    #EndFunction

    #Checks OrderBook for potential Transactions
    def Check_OrderBook_For_Potential_TXN(self):

    #EndFunction

    #Iterates through Blockchain to get latest Balance
    def Get_Merchant_Current_Balance(self, merchant_public_key):
        
    #EndFunction

    def Run(self):

        #Main loop
        while True:


        #EndWhile
    #EndFunction
#EndClass

def main():
    ip = "localhost"
    server_port = 2600
    client_port = 2500
    market = Market(ip, server_port, client_port)
    market.Run()
#EndMain

if __name__ == "__main__":
    main()
#EndIf