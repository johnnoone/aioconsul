#!/usr/bin/env python

from setuptools import setup

setup(
    name='aioconsul',
    version='0.1',
    description='Use consul with asyncio',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://github.com/johnnoone/aioconsul',
    packages=[
        'aioconsul'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=[
        'aiohttp==0.14.4'
    ],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    }
)
