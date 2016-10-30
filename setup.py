#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

with open('README.rst') as file:
    long_description = file.read()

setup(
    name="aioconsul",
    long_description=long_description,
    version=versioneer.get_version(),
    description='async/await client for the Consul HTTP API',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='http://aio.errorist.io/aioconsul',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Clustering',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    install_requires=[
        'aiohttp>=1.0.2',
        'python-dateutil>=2.5.3',
        'pyhcl>=0.2.1',
        'wheel>0.25.0'
    ],
    license='BSD',
    cmdclass=versioneer.get_cmdclass()
)
