"""

CPU Bound Task: Computing Factorial of large Number 

"""

import multiprocessing
import math
import sys
import time

sys.set_int_max_str_digits(100000)

# function to compute of given larger number 

def compute_fact(num):

    print(f"Computing Factorial of {num}")
    rslt = math.factorial(num)
    print(f"factorial of {num} is {rslt}")
    return rslt


if __name__ == "__main__":
    nums = [5000,6000,7000,8000]

    start_time = time.time()

    processes = []

    for num in nums:
        p = multiprocessing.Process(target=compute_fact, args=(num, ))
        processes.append(p)
        p.start()


    for p in processes:
        p.join()

    print("Total Time:", time.time() - start_time)


    ''' 
    #Each process is independent

Own memory, own Python interpreter
One process cannot modify variables in another process

# Function calls run “in parallel”

Even though it’s the same function, each process executes it with its own argument

# Background execution

When you call p.start(), the process runs asynchronously, in the background
The main process continues creating more processes

# join() just waits

It doesn’t start or stop the function
It waits for that specific process to finish



Main process:        |----> creates Process1 -> compute_fact(5000)
                      |----> creates Process2 -> compute_fact(6000)
                      |----> creates Process3 -> compute_fact(7000)
                      |----> creates Process4 -> compute_fact(8000)

Process1: compute_fact(5000) running independently
Process2: compute_fact(6000) running independently
Process3: compute_fact(7000) running independently
Process4: compute_fact(8000) running independently


### if same is runned using Multi threading 

Multiprocessing: (CPU-bound)
Main ──► P1(5000!) ──► Core1
      ──► P2(6000!) ──► Core2
      ──► P3(7000!) ──► Core3
      ──► P4(8000!) ──► Core4
True parallel, separate memory

Multithreading: (CPU-bound)
Main ──► T1(5000!)
      ──► T2(6000!)
      ──► T3(7000!)
      ──► T4(8000!)
Only one runs at a time due to GIL
Shared memory
Slower for CPU tasks

Multithreading: (I/O-bound)
Main ──► T1(waiting)
      ──► T2(waiting)
      ──► T3(waiting)
      ──► T4(waiting)
While T1 waits, CPU runs T2/T3/T4
Much faster for network/file operations
    
    '''