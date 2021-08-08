# ByteMarket
ByteMarket is a blockchain based decentralized exchange for buying & selling goods. ByteMarket adopts a unique order-book set up which allows buyers & sellers to place bid and ask prices using a price-priority algorithm to trade the goods.
## Requirements
Your machine should have the latest version of python3 installed for proper working.
## Running the Application
pip install cryptography

## Assumptions
•	Each buyer and seller, can only place one bid/ask price placed in the order book at a time.
•	There are a fixed number of coins, as mentioned in the coinbase of the genesis block, which are allotted to the clients (both buyers & sellers) when they enter the market place.

## Description
Client.py: This maintains the client side of the application. Buyers/Sellers come to this portal and after registering can place their bid/ask price.
Market.py: This maintains the order book and constantly performs read and write operations in the order book. The price-priority algorithm checks for possible matches & if found, sends the transaction request to the miner.
Miner.py: The miner receives a transaction request for the market and forms a block with the received data. The block is then mined using the proof of work algorithm to find a suitable nonce for the BlockHash. Once the block is mined, it is added to the Blockchain and broadcasted to all the nodes.

