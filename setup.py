from setuptools import setup, find_packages
import os

setup(name = 'arduinostepper',
    packages = find_packages('.'),
    package_dir = {'arduinostepper': 'arduinostepper'},
    zip_safe = False)
