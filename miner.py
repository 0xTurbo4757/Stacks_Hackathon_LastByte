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

    MINER_MINING_DIFFICULTY_LEVEL = 3

    MINER_BLOCKCHAIN_PREVIOUS_HASH_STR = "PrevHash"
    MINER_BLOCKCHAIN_DATA_STR = "Data"
    MINER_BLOCKCHAIN_NONCE_STR = "Nonce"
    MINER_BLOCKCHAIN_COINBASE_STR = "CoinBase"

    MINER_BLOCKCHAIN_GENESIS_PREV_HASH = "00000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, server_ip, server_port):
        self.blocknumber = 1
        self.previousBlockHash = Miner.MINER_BLOCKCHAIN_GENESIS_PREV_HASH
        self.transactionSarib = "Sender2,Reciever2,Price2"
        
        #Final BlockChain to send to everyone
        self.Entire_BlockChain = []
        self.Mining_Difficulty_Level = Miner.MINER_MINING_DIFFICULTY_LEVEL

        # Socket Handling As Server For market.py & client.py
        self.ServerForClient_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind((server_ip, server_port))
        self.Market_Address = ()
    #EndFunction

    def Check_if_Correct_Hash_Found_by_Difficulty_Level(self, target_hash, target_zeros):
        try:
            target_hash_found = (int(target_hash[0:target_zeros]) == 0)
        except:
            target_hash_found = False
        #EndTry
        return target_hash_found
    #EndIf

    def Update_BlockChain(self):
        # Creating A Block
        testNonce = 0
        blockdata = {}

        # We are creating a Genesis Block
        # The CoinBase has the initial num
        if(self.blocknumber == 1):
            blockdata = {
                self.blocknumber: {
                    Miner.MINER_BLOCKCHAIN_PREVIOUS_HASH_STR : self.previousBlockHash,
                    Miner.MINER_BLOCKCHAIN_DATA_STR : self.transactionSarib,
                    Miner.MINER_BLOCKCHAIN_NONCE_STR : testNonce,
                    Miner.MINER_BLOCKCHAIN_COINBASE_STR : "Initially %s coins allotted to new client" % Miner.NEW_MERCHANT_FUND_AMOUNT
                }
            }
            print("\nInitiating The Genesis Block!")
            print("ByteMarket BlockChain, Initiated & Active\n")
        else:
            # The Block Is Not a Genesis Block
            blockdata = {
                self.blocknumber: {
                    Miner.MINER_BLOCKCHAIN_PREVIOUS_HASH_STR : self.previousBlockHash,
                    Miner.MINER_BLOCKCHAIN_DATA_STR : self.transactionSarib,
                    Miner.MINER_BLOCKCHAIN_NONCE_STR : testNonce
                }
            }
        #EndIf

        # MINING THE BLOCK
        currentBlockHash = hashFunction.hash_object(blockdata)
        # self.blocknumber = self.blocknumber + 1
        # Our Proof Of Work Is Based on Finding the Nonce for which the first two digits of the BlockHash are 0
        # CONSENSUS IMPLEMENTED
        # Implementing Proof Of WORK
        print("Mining The Block to Find the Correct Nonce!")
        while(not(self.Check_if_Correct_Hash_Found_by_Difficulty_Level(currentBlockHash, self.Mining_Difficulty_Level))):   
            # Finding CORRECT NONCE
            testNonce = testNonce + 1
            # Starting from a testNonce and WORKING to find the nonce giving the first two digits of SHA As 0
            blockdata[self.blocknumber][Miner.MINER_BLOCKCHAIN_NONCE_STR] = testNonce
            currentBlockHash = hashFunction.hash_object(blockdata)
        print("The Block Is Mined, Adding the Block to the Central Ledger")
        print(currentBlockHash)
        # THE BLOCK IS NOW MINED

        # Writing it to BlockChain.JSON which is the public ledger file

        # ADDING THE BLOCK TO THE CENTRAL LEDGER // BlockChain - WHICH IS A JSON HERE

        # Serializing json
        json_object = json.dumps(blockdata, indent=4)
        # Writing to sample.json
        with open("BlockChain.json", "r+") as file:
            data = json.load(file)
            # Appending to the BlockChain
            data.update(blockdata)
            file.seek(0)
            json.dump(data, file, indent=4)

        
        f = open("BlockChain.json","r+")
        self.Entire_BlockChain = json.load(f)
        f.close()
        print("\nEntire BlockChain: \n{}\n".format(str(self.Entire_BlockChain)))

        self.blocknumber = self.blocknumber + 1
        self.previousBlockHash = currentBlockHash
    #EndFunction

    def Handle_Incoming_Request_from_Client(self):
        incomming_UDP_Data = self.ServerForClient_Socket.recvfrom(Miner.UDP_DATA_BUFFER_SIZE)
        Data = incomming_UDP_Data[0].decode(Miner.DATA_ENCODING_FORMAT)
        Client_Address = incomming_UDP_Data[1]

        if (len(Data)):
            print("\nReceived: '{}' from 'localhost:{}'".format(Data, Client_Address[1]))
            #If Client Expects Latest BlockChain, send it to them
            if (Data == Miner.MINER_BLOCKCHAIN_REQUEST_STR):
                print("\nSending: '{}' to 'localhost:{}'".format("BlockChain", Client_Address[1]))
                self.ServerForClient_Socket.sendto(str(self.Entire_BlockChain).encode(Miner.DATA_ENCODING_FORMAT), Client_Address)
            #Market sent TXN Request
            elif (Data[0:3] == "TXN"):
                #Save Market_Addr
                self.Market_Address = Client_Address
                #Get TXN Request
                self.transactionSarib = Data[4:]
                print("\nGot TXN Request: {} from 'localhost:{}'".format(self.transactionSarib, Client_Address[1]))
                #Initiate Mining

                #print("transactionSarib was {}".format(self.transactionSarib))
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

    #Empty Json file to prevent errors
    f = open("BlockChain.json","w")
    f.write("{\n\t\n}")
    f.close()
    
    ip = "localhost"
    server_port = 2500
    miner = Miner(ip, server_port)
    miner.RunMiner()
# EndMain

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nExiting Miner\nGoodBye!\n")
        exit()
    #EndTry
#EndIf