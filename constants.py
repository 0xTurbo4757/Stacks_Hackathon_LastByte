#General Settings
DATA_ENCODING_FORMAT = "utf-8"                              #Data Encoding format for socket programming
UDP_DATA_BUFFER_SIZE = 32768                                #UDP Incomming data buffer size
NEW_MERCHANT_FUND_AMOUNT = 100                              #Funds given to new merchants

#Merchant Settings
MERCHANT_USERNAME_STR = "m_Username"                        #JSON KEY: Merchant User Name
MERCHANT_HASHED_USERNAME_STR = "m_HashedUsername"           #JSON KEY: Merchant Hashed User Name
MERCHANT_PRIVATE_KEY_STR = "m_PrivKey"                      #JSON KEY: Merchant Private Key
MERCHANT_PUBLIC_KEY_STR = "m_PubKey"                        #JSON KEY: Merchant Public Key
MERCHANT_SIGNATURE_STR = "m_Sign"                           #JSON KEY: Merchant Signature
MERCHANT_TYPE_STR = "m_Type"                                #JSON KEY: Merchant Type
MERCHANT_COMODITY_STR = "m_Item"                            #JSON KEY: Merchant Item to sell/buy
MERCHANT_PRICE_STR = "m_Price"                              #JSON KEY: Merchant Item Price
MERCHANT_IP_STR = "m_nIP"                                   #JSON KEY: Merchant IP Address
MERCHANT_PORT_STR = "m_nPort"                               #JSON KEY: Merchant Port
MERCHANT_TYPE_BUYER_STR = "Buyer"                           #JSON VAL: Merchant Type: Buyer
MERCHANT_TYPE_SELLER_STR = "Seller"                         #JSON VAL: Merchant Type: Seller

#Request Strings
MARKET_NEW_MERCHANT_REQUEST_STR = "NEW"
MARKET_NEW_ORDER_REQUEST_STR = "ODR"
MINER_TXN_REQUEST_STR = "TXN"
MINER_BLOCKCHAIN_REQUEST_STR = "chain"                      #When this is sent to the miner, it sends the BlockChain Back
CLIENT_ORDERBOOK_REQUEST_STR = "order"                      #When this is sent to the market, it sends the OrderBook Back

#File Names
MARKET_ORDERBOOK_FILE_NAME = "OrderBook.txt"
USERDATABASE_FILE_NAME = "clients.json"                     #Filename of UserDataBase file

#Miner Settings
MINER_DEFAULT_ADDRESS = 0                                   #Default miner address
MINER_MINING_DIFFICULTY_LEVEL = 3                           #
MINER_BLOCKCHAIN_PREVIOUS_HASH_STR = "PrevHash"             #
MINER_BLOCKCHAIN_DATA_STR = "Data"                          #
MINER_BLOCKCHAIN_NONCE_STR = "Nonce"                        #
MINER_BLOCKCHAIN_COINBASE_STR = "CoinBase"                  #
MINER_BLOCKCHAIN_GENESIS_PREV_HASH = "0000000000000000000000000000000000000000000000000000000000000000"