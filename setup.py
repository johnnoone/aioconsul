#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

setup(
    name="aioconsul",
    version=versioneer.get_version(),
    description='Consul wrapper for asyncio',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://lab.errorist.zyz/aio/aioconsul',
    packages=find_packages(),
    keywords=[
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
        'aiohttp>=1.0.2',
        'python-dateutil>=2.5.3',
        'blinker>=1.4',
        'pyhcl>=0.2.1',
        'wheel>0.25.0'
    ],
    cmdclass=versioneer.get_cmdclass()
)
