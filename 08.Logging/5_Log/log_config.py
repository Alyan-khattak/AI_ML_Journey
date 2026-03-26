
#######################################################
#  THIS IS MY LOG Config FILE ( CONFIGURATION FOR LOGGING IS WRIITEN HERE)
######################################################

import logging



# -------- FORMATTER --------
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ================== AUTH LOGGER ==================
auth_logger = logging.getLogger("Auth")
auth_logger.setLevel(logging.DEBUG)

# now create FIle Handlers set its fromat and add it to logger
#creating File Handlers
auth_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/5_Log/Auth_logs.log")
auth_console = logging.StreamHandler()

# set fromating to Handler
auth_file.setFormatter(formatter)
auth_console.setFormatter(formatter)

#add HAndlers to Logger
auth_logger.addHandler(auth_file)
auth_logger.addHandler(auth_console)



# ================== DATABASE LOGGER ==================
db_logger = logging.getLogger("DataBase")
db_logger.setLevel(logging.DEBUG)

# create file Handler , set its fromat and add it to logger
db_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/5_Log/Database_logs.log")
db_console = logging.StreamHandler()

db_logger.addHandler(db_file)
db_logger.addHandler(db_console)


# ================== NETWORK LOGGER ==================
net_logger = logging.getLogger("Network")
net_logger.setLevel(logging.WARNING)

net_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/5_Log/network.log")
net_console = logging.StreamHandler()

net_logger.addHandler(net_file)
net_logger.addHandler(net_console)