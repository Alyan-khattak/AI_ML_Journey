# ═══════════════════════════════════════════════════════════════════
# setup.py
# ═══════════════════════════════════════════════════════════════════
# Python project ko installable package banata hai.
# pip install -e . chalane pe yeh file run hoti hai.
# find_packages() → src/ folder dhundhta hai aur register karta hai
# get_requirements() → requirements.txt padhta hai aur list return karta hai
#
# IMP: Krish Naik ka style — requirements.txt se dynamically read karta hai
# Tumhara pehla wala → hardcoded list tha install_requires mein
# Yeh better hai — requirements.txt update karo, setup.py same rehta hai
###==============================================================

from setuptools import find_packages, setup
from typing import List

# ── FUNCTION: get_requirements ────────────────────────────────────
def get_requirements() -> List[str]:
    """
    requirements.txt file padhta hai aur packages ki list return karta hai.

    Returns:
        List[str] : e.g. ["pandas", "numpy", "scikit-learn", ...]

    IMP: '-e .' ko ignore karta hai
         '-e .' = editable install ka symbol
         agar yeh list mein reh jaaye → pip error aata hai
         kyunki '-e .' ek package naam nahi hai
    """

    requirement_lst: List[str] = []   # khali list — baad mein fill hogi

    try:
        with open('requirements.txt', 'r') as file:
            # requirements.txt ki sab lines padhna
            lines = file.readlines()
            # lines = ["pandas\n", "numpy\n", "scikit-learn\n", "-e .\n"]

            for line in lines:
                requirement = line.strip()
                # .strip() → whitespace aur \n remove karta hai
                # "pandas\n" → "pandas"

                # IMP: do cheezein ignore karo:
                # 1. empty lines ("")
                # 2. '-e .' — editable install marker, package nahi
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst
    # → ["pandas", "numpy", "scikit-learn", "mlflow", ...]


# ── SETUP ─────────────────────────────────────────────────────────
setup(
    name="NetworkSecurity",          # package ka naam (pip install NetworkSecurity)
    version="0.0.1",                 # version tag
    author="M.Alyan",
    author_email="alyankhattake@gmail.com",
    packages=find_packages(),        # automatically sab packages dhundho
                                     # (explanation neeche)
    install_requires=get_requirements()  # requirements.txt se list milti hai
                                         # pip automatically install karega
)


# ─────────────────────────────────────────────────────────────────
# EXPLANATIONS
# ─────────────────────────────────────────────────────────────────

# ── 1. find_packages() kya hai? ───────────────────────────────────
#
# find_packages() → project mein sab Python packages dhundhta hai
# "Package" = koi bhi folder jisme __init__.py file ho
#
# Example:
# networksecurity/
# ├── __init__.py          ← yeh hai → package hai 
# ├── components/
# │   └── __init__.py      ← yeh hai → package hai 
# └── utils/
#     └── __init__.py      ← yeh hai → package hai 
#
# find_packages() → ["networksecurity",
#                    "networksecurity.components",
#                    "networksecurity.utils"]
#
# Agar __init__.py nahi hai → folder ignore ho jaata hai
# Isliye har subfolder mein __init__.py banana zaroori hai
#
# ─────────────────────────────────────────────────────────────────

# ── 2. List kya hai? ──────────────────────────────────────────────
#
# from typing import List
#
# List = Python ka type hint — batata hai function kya return karega
# Python dynamically typed hai — List zaroori nahi
# lekin code readable aur professional lagta hai
#
# List[str] = strings ki list
# List[int] = integers ki list
# List[float] = floats ki list
#
# Examples:
# List[str]   → ["pandas", "numpy", "scikit-learn"]
# List[int]   → [1, 2, 3, 4]
# List[float] → [0.1, 0.5, 0.88]
#
# ─────────────────────────────────────────────────────────────────

# ── 3. def get_requirements() -> List[str]: kya hai? ─────────────
#
# -> List[str] = RETURN TYPE ANNOTATION
# Batata hai yeh function kya return karega
#
# Syntax:
# def function_name(params) -> return_type:
#
# Examples:
# def add(a: int, b: int) -> int:          ← int return karega
# def get_name() -> str:                    ← string return karega
# def get_scores() -> List[float]:          ← list of floats
# def get_requirements() -> List[str]:      ← list of strings
#
# IMP: yeh sirf hint hai — Python enforce nahi karta
#      agar tum float return karo List[str] mein → Python crash nahi karega
#      lekin VS Code / type checkers warn karenge
#      professional code mein hamesha type hints likhte hain
# ─────────────────────────────────────────────────────────────────