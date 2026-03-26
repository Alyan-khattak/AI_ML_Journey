
from logger import logging  # import logging from our logging file 

def divide(a,b):
    logging.info(f"Diving {a} by {b}")

    if b == 0:
        logging.error("Division by zero Attempted! ")
        return None
    
    return a/b


def main():

    divide(10,2)
    divide(5,0)
    divide(7,1)


if __name__ == "__main__":
    main()

