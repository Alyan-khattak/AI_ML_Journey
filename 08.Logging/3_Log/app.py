
from logger import logging
# Function 1: Divide two numbers
def divide(a,b):
    # info log saved in app.log file
    logging.info(f"Dividing {a} by {b}")

    if b == 0:
        logging.error("Division by zero")
        return None
    
    rslt = a/b
    logging.debug(f"Division Result : {rslt}")
    return rslt

# Function 2: Login simulation
def login(user, password):

    logging.info(f"User {user} is Attempting to Log in ")

    if user == "admin" and password == "admin":
        logging.info(f"User '{user}' is sucessfully Logged in")
        return True
    else:

        logging.warning(f"Failed Login attempt for User '{user}'")
        return False
    


# Function 3: Process a list of numbers
def process_nmbrs(nums):
    logging.info(f"Processing list: {nums}")

    total = 0
    for num in nums:
        if num < 0:
            logging.warning(f"Negative nmbr Encountered: {num}")
        total += num
        logging.debug(f"total sum: {total}")
        return total
    

# Function 4: Simulate a simple file read
def read_file(filename):
    logging.info(f"Atempting to read file: {filename}")

    try:
        with open(filename, "r") as file:
            content = file.read()
            logging.debug(f"File Conetent length: {len(content)}")
            return content
    except FileNotFoundError as ex:
        logging.error(f"File: {filename} not Found")
        return None
    

          

# Main function to run all examples
def main():
    # Test divide
    divide(10, 2)
    divide(5, 0)
    divide(7, 1)

    # Test login
    login("admin", "admin123")
    login("user1", "pass123")

    # Test number processing
    process_nmbrs([10, 20, -5, 15, -2])

    # Test file reading
    read_file("example.txt")  # Try a file that may not exist
    read_file("logger.py")  # logger.py where I have written config

if __name__ == "__main__":
    main()