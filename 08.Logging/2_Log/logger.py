

#######################################################
#  THIS IS MY LOGGER FILE ( CONFIGURATION FOR LOGGING IS WRIITEN HERE)
######################################################


import logging

logging.basicConfig(
    level=logging.DEBUG,
    format= "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt= "%Y - %m - %d %H:%M:%S",
    filename="/home/aizen/AI_ML/08.Logging/2_Log/app.log", # logs in this app
    filemode="w"
)

