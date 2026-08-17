# exception.py — Global custom exception handler.
# Wraps Python's built-in Exception to also capture FILE NAME + LINE NUMBER.
# Import and use across entire project instead of plain Exception.

import sys

def error_message_detail(error, error_detail: sys):
    # exc_info() returns (type, value, traceback) — we only need traceback
    _, _, exc_tb = error_detail.exc_info()

    # traceback object → frame → code object → filename
    file_name = exc_tb.tb_frame.f_code.co_filename

    # build detailed error string with file, line, message
    error_message = "error occured in python script name [ {0} ], line number [ {1} ] error message [ {2} ]".format(
        file_name,
        exc_tb.tb_lineno,   # exact line number where crash happened
        str(error)
    )

    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)   # init base Exception with message
        # override message with detailed version (file + line + error)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)
        
    # dundder method
    def __str__(self):
        return self.error_message   # when printed, shows full detail



# ─────────────────────────────────────────────
# DRY RUN — what happens when this triggers:
#
# suppose in train.py line 42:
#   raise CustomException("model file not found", sys)
#
# 1. CustomException.__init__ called
#      error_message = "model file not found"
#      error_detail  = sys
#
# 2. calls error_message_detail("model file not found", sys)
#      sys.exc_info() returns traceback of current exception
#      exc_tb.tb_frame.f_code.co_filename  →  "train.py"
#      exc_tb.tb_lineno                    →  42
#
# 3. builds string:
#      "error occured in python script name [ train.py ],
#       line number [ 42 ] error message [ model file not found ]"
#
# 4. print(e)  or  logging.info(e)  →  prints that full string
# ─────────────────────────────────────────────