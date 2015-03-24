#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    content = file.read()

setup(
    name='aioconsul',
    version='0.2',
    description='Consul wrapper for asyncio',
    long_description=content,
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://github.com/johnnoone/aioconsul',
    packages=[
        'aioconsul'
    ],
    keywords = [
        'infrastructure',
        'asyncio',
        'service discovery',
        'health checking',
        'key/value store'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Clustering',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    install_requires=[
        'aiohttp>=0.14.4'
    ],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    }
)
