from log_config import logging

# Get ur logger here : Give them same names as Config

auth_logger = logging.getLogger("Auth")
db_logger = logging.getLogger("Database")
net_logger = logging.getLogger("Network")


# -------- FUNCTIONS --------

def login(user, password):
    auth_logger.info(f"Login attempt for User : {user}")
    if user == "admin" and password == "admin":
        auth_logger.debug(f"user: {user} Logged in Successfully")
        return True
    else:
        auth_logger.warning(f"Invalid Credentail for {user}")
        return False
    

def fetch_data():
    db_logger.debug("Executing SELECT Querry")
    db_logger.info("Fectjing Data from Data base")

    db_logger.error("DAtabase Connection Failed")

def call_api():
    net_logger.info("sending API req")
    net_logger.warning("API response is slow")
    net_logger.error("API req Failed")


# -------- MAIN --------

def main():
    login("admin", "wrong_pass")
    login("admin", "admin")

    fetch_data()
    call_api()


if __name__ == "__main__":
    main()