# setup.py — OLD way to package a Python project.
# Tells pip: project name, version, author, and what to install.
# Run: pip install .   →   pip reads this file and installs everything.
# Modern replacement: pyproject.toml (see bottom)


# find_packages() scan every folder in project for __init__.py file.
# Folder got __init__.py = Python treat it as package = gets included in install.
# Folder got NO __init__.py = ignored.


from setuptools import find_packages, setup

HYPEN_E_DOT = '-e .'

def get_requirements(file_path:str)->list[str]:
    '''
        this function will return list of requirements
    '''
    requirements = []
    with open(file_path) as f:
        requirements = f.readlines()
        [req.replace("\n", "") for req in requirements]
    # in requirement.txt we have a "-e ." we dont need to install it     
    if HYPEN_E_DOT in requirements: 
        requirements.remove(HYPEN_E_DOT)

    return requirements

setup(
    name="mlproject",           # package name (used in pip install)
    version="0.0.1",            # version tag
    author="M.Alyan",
    author_email="alyankhattake@gmail.com",
    packages=find_packages(),   # auto-finds all folders with __init__.py
    install_requires=get_requirements('requirements.txt')
)




# ─────────────────────────────────────────────
# MODERN WAY: pyproject.toml  (replaces setup.py)
# Create file named pyproject.toml in project root:
#
# [build-system]
# requires = ["setuptools"]
# build-backend = "setuptools.backends.legacy:build"
#
# [project]
# name = "mlproject"
# version = "0.0.1"
# authors = [{name = "M.Alyan", email = "alyankhattake@gmail.com"}]
# dependencies = ["pandas", "numpy", "seaborn"]
#
# HOW TO USE (same for both):
#   pip install .          → installs package locally
#   pip install -e .       → editable install (code changes reflect instantly)
# ─────────────────────────────────────────────