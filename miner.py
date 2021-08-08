# Miner Code Here
# Zain
# sarib gamer
import hashFunction
import json
import socket

class Miner:
    MINER_BLOCKCHAIN_REQUEST_STR = "chain"
    DATA_ENCODING_FORMAT = "utf-8"
    UDP_DATA_BUFFER_SIZE = 8192
    NEW_MERCHANT_FUND_AMOUNT = 100

    def __init__(self, server_ip, server_port):
        self.blocknumber = 1
        self.previousBlockHash = "00000000000000000000000000000000000000000000000000000000000000000"
        self.transactionSarib = "Sender2,Reciever2,Price2"
        self.blockdata = {}

        # Socket Handling As Server For market.py & client.py
        self.ServerForClient_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind((server_ip, server_port))
        self.Market_Address = ()
    #EndFunction

    def Update_BlockChain(self):
        # LOOP!
        # "PKEY,PKEY,PRICE"
        self.transactionSarib = "Sender2,Reciever2,Price2"

        # Creating A Block
        testNonce = 0
        self.blockdata = {}
        # We are creating a Genesis Block
        # The CoinBase has the initial num
        if(self.blocknumber == 1):
            self.blockdata = {
                self.blocknumber: {
                    "Previous Hash: ": "00000000",
                    "Data: ": self.transactionSarib,
                    "Nonce: ": testNonce,
                    "CoinBase: ": "Initially 1000 coins alloted to clients"
                }
            }
            print("Initiating The Genesis Block!")
            print("ByteMarket BlockChain, Initiated & Active")
        else:
            # The Block Is Not a Genesis Block
            self.blockdata = {
                self.blocknumber: {
                    "Previous Hash: ": self.previousBlockHash,
                    "Data: ": self.transactionSarib,
                    "Nonce: ": testNonce
                }
            }

        # MINING THE BLOCK
        currentBlockHash = hashFunction.hash_object(self.blockdata)
        # self.blocknumber = self.blocknumber + 1
        # Our Proof Of Work Is Based on Finding the Nonce for which the first two digits of the BlockHash are 0
        # CONSENSUS IMPLEMENTED
        # Implementing Proof Of WORK
        print("Mining The Block to Find the Correct Nonce!")
        while((currentBlockHash[0] != "0") or (currentBlockHash[1] != "0")):
            # Finding CORRECT NONCE
            testNonce = testNonce + 1
            # Starting from a testNonce and WORKING to find the nonce giving the first two digits of SHA As 0
            self.blockdata[self.blocknumber]['Nonce: '] = testNonce
            currentBlockHash = hashFunction.hash_object(self.blockdata)
        print("The Block Is Mined, Adding the Block to the Central Ledger")
        print(currentBlockHash)
        # THE BLOCK IS NOW MINED

        # Writing it to BlockChain.JSON which is the public ledger file

        # ADDING THE BLOCK TO THE CENTRAL LEDGER // BlockChain - WHICH IS A JSON HERE

        # Serializing json
        json_object = json.dumps(self.blockdata, indent=4)
        # Writing to sample.json
        with open("BlockChain.json", "r+") as file:
            data = json.load(file)
            # Appending to the BlockChain
            data.update(self.blockdata)

            file.seek(0)

            json.dump(data, file, indent=4)

        self.blocknumber = self.blocknumber + 1
        self.previousBlockHash = currentBlockHash
    #EndFunction

    def Handle_Incoming_Request_from_Client(self):
        incomming_UDP_Data = self.ServerForClient_Socket.recvfrom(Miner.UDP_DATA_BUFFER_SIZE)
        Data = incomming_UDP_Data[0].decode(Miner.DATA_ENCODING_FORMAT)
        Client_Address = incomming_UDP_Data[1]

        if (len(Data)):
            print("\n\nReceived Data: {}\n\n".format(Data))
            #If Client Expects Latest BlockChain, send it to them
            if (Data == Miner.MINER_BLOCKCHAIN_REQUEST_STR):
                self.ServerForClient_Socket.sendto(self.blockdata.encode(Miner.DATA_ENCODING_FORMAT), Client_Address)
            #Market sent TXN Request
            elif (Data[0:3] == "TXN"):
                #Save Market_Addr
                self.Market_Address = Client_Address
                #Get TXN Request
                self.transactionSarib = Data[4:]
                print("Got TXN Request: {}".format(self.transactionSarib))
                #Initiate Mining
                self.Update_BlockChain()
            #EndIf
        #EndIf
    #EndFunction

    def RunMiner(self):
        while True:
            self.Handle_Incoming_Request_from_Client()
        #EndWhile
    #EndFunction
#EndClass

def main():
    ip = "localhost"
    server_port = 2500
    miner = Miner(ip, server_port)
    miner.RunMiner()
# EndMain

if __name__ == "__main__":
    main()
# EndIf