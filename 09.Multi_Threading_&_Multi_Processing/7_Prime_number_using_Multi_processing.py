import multiprocessing
import time
import math

# Function to check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Function to process a range of numbers
def find_primes(start, end):
    primes = []
    for num in range(start, end):
        if is_prime(num):
            primes.append(num)
    print(f"Primes in range {start}-{end} computed. Total: {len(primes)}")
    return primes

if __name__ == "__main__":
    start_time = time.time()

    # Split work into 4 ranges
    ranges = [(1, 50000), (50000, 100000), (100000, 150000), (150000, 200000)]
    processes = []

    for r in ranges:
        p = multiprocessing.Process(target=find_primes, args=(r[0], r[1]))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("All prime calculations done in:", time.time() - start_time)