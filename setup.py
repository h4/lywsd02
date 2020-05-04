from setuptools import find_packages, setup

VERSION = '0.0.9'

setup(
    name='lywsd02',
    version=VERSION,
    packages=find_packages(exclude=("tests",)),
    url='https://github.com/h4/lywsd02',
    license='MIT',
    author='h4',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=['bluepy==1.3.0'],
    author_email='mikhail.baranov@gmail.com',
    description='Lywsd02 BLE sendor Library',
    long_description_content_type='text/x-rst',
    long_description='Library to read data from Mi Temperature and Humidity Sensor (E-Inc version with Clock)',
)
