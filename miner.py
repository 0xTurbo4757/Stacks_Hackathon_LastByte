# Miner Code Here
# Zain
# sarib gamer
import hashFunction
import json

blocknumber = 1
previousBlockHash = ""

# LOOP!

# "PKEY,PKEY,PRICE"
transactionSarib = "Sender1,Reciever1,Price1"

# Creating A Block
testNonce = 0
blockdata = {}
# We are creating a Genesis Block 
# The CoinBase has the initial num
if(blocknumber == 1):
    blockdata = {
                blocknumber : {
                    "Previous Hash: ": "00000000",
                    "Data: ": transactionSarib,
                    "Nonce: ": testNonce,
                    "CoinBase: ": "Initially 1000 coins alloted to clients" 
                }
    }
else:
# The Block Is Not a Genesis Block
    blockdata = {
                blocknumber : {
                    "Previous Hash: ": previousBlockHash,
                    "Data: ": transactionSarib,
                    "Nonce: ": testNonce
                }
    }
    blocknumber = blocknumber + 1;


# MINING THE BLOCK
currentBlockHash = hashFunction.hash_object(blockdata)

# Our Proof Of Work Is Based on Finding the Nonce for which the first two digits of the BlockHash are 0
# CONSENSUS IMPLEMENTED
# Implementing Proof Of WORK
print("Mining The Block to Find the Correct Nonce!")
while( (currentBlockHash[0] != "0") or (currentBlockHash[1] != "0") ):
    # Finding CORRECT NONCE
    testNonce = testNonce + 1
    # Starting from a testNonce and WORKING to find the nonce giving the first two digits of SHA As 0
    blockdata[blocknumber]['Nonce: '] = testNonce
    currentBlockHash = hashFunction.hash_object(blockdata)
print("The Block Is Mined, Adding the Block to the Central Ledger")
# THE BLOCK IS NOW MINED

# Writing it to BlockChain.JSON which is the public ledger file

# ADDING THE BLOCK TO THE CENTRAL LEDGER // BlockChain - WHICH IS A JSON HERE

# Serializing json
json_object = json.dumps(blockdata, indent=4)
# Writing to sample.json
with open("BlockChain.json", "r+") as file:
    data = json.load(file)
    #Appending to the BlockChain
    data.update(blockdata)
    
    file.seek(0)
    
    json.dump(data, file, indent = 4)












