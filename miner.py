# Miner Code Here
# Zain
# sarib gamer
import hashFunction
import json

blocknumber = 3
previousBlockHash = ""


# "PKEY,PKEY,PRICE"
transactionSarib = "Sender3,Reciever3,Price3"




# Creating A Block
testNonce = 0
blockdata = {}
# We are creating a Genesis Block 

if(blocknumber == 1):
    blockdata = {
                blocknumber : {
                    "Previous Hash: ": "00000000",
                    "Data: ": transactionSarib,
                    "Nonce: ": testNonce
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

# Writing it to JSON

# Serializing json
json_object = json.dumps(blockdata, indent=4)
# Writing to sample.json

with open("BlockChain.json", "r+") as fi:
    data = json.load(fi)
    data.update(blockdata)
    fi.write('/n')
    fi.seek(0)
    json.dump(data, fi, indent = 4)


# Implementing Proof Of WORK
# Finding CORRECT NONCE

nonce = 1;






