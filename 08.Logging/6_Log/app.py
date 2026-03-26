from log_config import logging

# -------- GET CUSTOM LOGGERS --------
auth_logger = logging.getLogger("Auth")
db_logger = logging.getLogger("Database")
net_logger = logging.getLogger("Network")






# -------- FUNCTIONS --------
# Login System

def login(user, pss):
    logging.info("login Func Called") # roor logger

    auth_logger.info(f"user : {user} attempted Login")
    if user == "admin" and pss == "admin":
        auth_logger.debug(f"user {user} logged in Succesfully")
        return True
    else:
        auth_logger.warning(f"Wrong Password for user {user}")
        return False
    


#Add DATA
data_store = []

def add_data(value):
    logging.debug("Adding data to Database") # root 

    try:
        data_store.append(value)
        db_logger.info(f"added value {value}")
    except Exception as e:
        db_logger.error(f"error adding data {e}")

#Fetch Data

def fetch_data():
    logging.debug("Fetching Data from DB") # root

    if not data_store:
        db_logger.warning("Database is empty")
        return []
    
    db_logger.info(f"Fetched Data: {data_store}")
    return data_store


# DELETE DATA
def delete_data(value):
    logging.debug("Deleting data")
    
    if value in data_store:
        data_store.remove(value)
        db_logger.info(f"Deleted value: {value}")
    else:
        db_logger.error(f"Value {value} not found in database")



# API CALL SIMULATION
def call_api(endpoint):
    logging.info(f"Calling API: {endpoint}")
    
    if endpoint == "/users":
        net_logger.warning("API response is slow")
        return {"status": 200, "data": ["user1", "admin"]}
    
    elif endpoint == "/error":
        net_logger.error("API request failed")
        return {"status": 500}
    
    else:
        net_logger.info("API request successful")
        return {"status": 200}


# SIMPLE CALCULATOR
def divide(a, b):
    logging.info("Divide function called")
    
    if b == 0:
        logging.error("Division by zero attempted")
        return None
    
    result = a / b
    logging.debug(f"Result: {result}")
    return result



# -------- MAIN --------

def main():
    # LOGIN TESTS
    login("admin", "admin")
    login("admin", "1234")
    login("unknown", "1234")

    # DATABASE TESTS
    add_data(10)
    add_data(20)
    fetch_data()
    delete_data(10)
    delete_data(50)

    # API TESTS
    call_api("/users")
    call_api("/error")
    call_api("/home")

    # CALCULATOR TEST
    divide(10, 2)
    divide(5, 0)


if __name__ == "__main__":
    main()
 



