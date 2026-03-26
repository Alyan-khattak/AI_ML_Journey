
# # Multi Processing
# - Allows us to run Processes in Parallel

# > CPU BOUND TASK: Tasks that are heavy: When your program spends more time doing heavy computations (not waiting)

# > Parallel Execution: When you want to use multiple CPU cores to run tasks truly in parallel 

# - Both will have Separate Memory

# ---
# ## syntax:
# ``` python 

# import multiprocessing

# # create process
# p = multiprocessing.Process(target=function_name)

# p.start()   # start process

# p.join()    # wait for process to finish


# # if function takes arguemnts
# def add(a, b):

# p = multiprocessing.Process(target=add, args=(5, 3))

# p.start()
# p.join()

# ```


###########################################################################
## NOTES IN 3_MultiProcessing.ipyb
############################################################################
### Multiprocessing wasnt running in ipynb file

import multiprocessing
import time

def fast():
    for i in range(3):
        time.sleep(1)
        print(f"Fast → {i}")

def slow():
    for i in range(3):
        time.sleep(2)
        print(f"Slow → {i}")

if __name__ == "__main__":

    p1 = multiprocessing.Process(target=fast)
    p2 = multiprocessing.Process(target=slow)

    start = time.time()

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Time:", time.time() - start)