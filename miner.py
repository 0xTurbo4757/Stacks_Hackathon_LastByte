import hashFunction
import json
import socket
import constants

class Miner:

# --------------------------------- CONSTRUCTOR

    def __init__(self, server_ip, server_port):
        
        self.Current_Block_Number = 1
        self.Previous_Block_Hash = constants.MINER_BLOCKCHAIN_GENESIS_PREV_HASH
        self.New_Block_Add_Request = ""
        
        #Final BlockChain to send to everyone as dictionary
        self.Entire_BlockChain = {}
        self.Mining_Difficulty_Level = constants.MINER_MINING_DIFFICULTY_LEVEL

        # Socket Handling As Server For market.py & client.py
        self.ServerForClient_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerForClient_Socket.bind((server_ip, server_port))
    #EndFunction

# --------------------------------- MINER

    def Check_if_Correct_Hash_Found_by_Difficulty_Level(self, target_hash, target_zeros):
        try:
            target_hash_found = (int(target_hash[0:target_zeros]) == 0)
        except:
            target_hash_found = False
        #EndTry
        return target_hash_found
    #EndIf

    def Generate_New_Block_Request(self, from_addr, to_addr, amount):
        return "%s,%s,%s" % (from_addr, to_addr, amount)
    #EndFunction

    def Update_BlockChain(self):
        # Creating A Block
        testNonce = 0
        blockdata = {}

        # We are creating a Genesis Block
        # The CoinBase has the initial num
        if(self.Current_Block_Number == 1):
            blockdata = {
                self.Current_Block_Number : {
                    constants.MINER_BLOCKCHAIN_PREVIOUS_HASH_STR : self.Previous_Block_Hash,
                    constants.MINER_BLOCKCHAIN_DATA_STR : self.New_Block_Add_Request,
                    constants.MINER_BLOCKCHAIN_NONCE_STR : testNonce,
                    constants.MINER_BLOCKCHAIN_COINBASE_STR : "Initially %s coins allotted to new client" % constants.NEW_MERCHANT_FUND_AMOUNT
                }
            }
            print("\nInitiating The Genesis Block!")
            print("ByteMarket BlockChain, Initiated & Active\n")
        else:
            # The Block Is Not a Genesis Block
            blockdata = {
                self.Current_Block_Number : {
                    constants.MINER_BLOCKCHAIN_PREVIOUS_HASH_STR : self.Previous_Block_Hash,
                    constants.MINER_BLOCKCHAIN_DATA_STR : self.New_Block_Add_Request,
                    constants.MINER_BLOCKCHAIN_NONCE_STR : testNonce
                }
            }
        #EndIf

        # MINING THE BLOCK
        currentBlockHash = hashFunction.hash_object(blockdata)
        # self.Current_Block_Number = self.Current_Block_Number + 1
        # Our Proof Of Work Is Based on Finding the Nonce for which the first two digits of the BlockHash are 0
        # CONSENSUS IMPLEMENTED
        # Implementing Proof Of WORK
        print("Mining The Block to Find the Correct Nonce!")
        while(not(self.Check_if_Correct_Hash_Found_by_Difficulty_Level(currentBlockHash, self.Mining_Difficulty_Level))):   
            # Finding CORRECT NONCE
            testNonce = testNonce + 1
            # Starting from a testNonce and WORKING to find the nonce giving the first two digits of SHA As 0
            blockdata[self.Current_Block_Number][constants.MINER_BLOCKCHAIN_NONCE_STR] = testNonce
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

        self.Current_Block_Number = self.Current_Block_Number + 1
        self.Previous_Block_Hash = currentBlockHash
    #EndFunction

# --------------------------------- HANDLERS

    def Handle_Incoming_Request_from_Client(self):
        incomming_UDP_Data = self.ServerForClient_Socket.recvfrom(constants.UDP_DATA_BUFFER_SIZE)
        Incomming_Data = incomming_UDP_Data[0].decode(constants.DATA_ENCODING_FORMAT)
        Client_Address = incomming_UDP_Data[1]

        if (len(Incomming_Data)):
            print("\nReceived: '{}' from 'localhost:{}'".format(Incomming_Data, Client_Address[1]))

            #If Client Expects Latest BlockChain, send it to them
            if (Incomming_Data == constants.MINER_BLOCKCHAIN_REQUEST_STR):
                print("\nSending: '{}' to 'localhost:{}'".format("BlockChain", Client_Address[1]))
                self.ServerForClient_Socket.sendto(str(self.Entire_BlockChain).encode(constants.DATA_ENCODING_FORMAT), Client_Address)
            
            #Market sent TXN Request
            #Incomming_Data format must be: TXN:FROM_ADDR,TO_ADDR,AMOUNT
            elif (Incomming_Data[0:3] == constants.MINER_TXN_REQUEST_STR):
                
                print("\nGot TXN Request: {} from 'localhost:{}'".format(Incomming_Data, Client_Address[1]))
                
                #Form TXN Request
                #Assume Market send a valid TXN in format: TXN:FROM_ADDR,TO_ADDR,AMOUNT
                #Pick up FROM_ADDR,TO_ADDR,AMOUNT
                self.New_Block_Add_Request = Incomming_Data[4:]
                
                #Initiate Mining
                #print("New_Block_Add_Request was {}".format(self.New_Block_Add_Request))
                self.Update_BlockChain()
            #EndIf
        #EndIf
    #EndFunction

# --------------------------------- RUN

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
    server_for_miner_port = 55000

    #Miner Object
    miner = Miner(ip, server_for_miner_port)

    #Run The Miner
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