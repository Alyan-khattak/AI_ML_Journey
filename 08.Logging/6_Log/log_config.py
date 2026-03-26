#######################################################
# LOGGER CONFIG FILE (Simple + Multiple Loggers)
#######################################################

import logging


# ================== SIMPLE LOGGING (ROOT LOGGER) ==================

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt= " %Y-%m-%d %H:%M:%S ",
    filename="/home/aizen/AI_ML/08.Logging/6_Log/app_logs.log",
    filemode="w"
)



# ================== MULTIPLE LOGGING (FOR MODULES) ==================

# ================== COMMON FORMATTER ==================
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ================== AUTH LOGGER ==================
auth_logger = logging.getLogger("Auth")
auth_logger.setLevel(logging.DEBUG)

# create file Handler , format it adn add it to logger
auth_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/6_Log/Auth_logs.log")
autth_console = logging.StreamHandler()

auth_logger.addFilter(auth_file)
auth_logger.addHandler(autth_console)


# ================== DATABASE LOGGER ==================
db_logger = logging.getLogger("Database")
db_logger.setLevel(logging.DEBUG)

db_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/6_Log/Database_logs.log")
db_console = logging.StreamHandler()

db_file.setFormatter(formatter)
db_console.setFormatter(formatter)

db_logger.addHandler(db_file)
db_logger.addHandler(db_console)



# ================== NETWORK LOGGER ==================
net_logger = logging.getLogger("Network")
net_logger.setLevel(logging.DEBUG)

net_file = logging.FileHandler("/home/aizen/AI_ML/08.Logging/6_Log/Net_logs.log")
net_console = logging.StreamHandler()

net_logger.addHandler(net_file)
net_logger.addHandler(net_console)