import os

from setuptools import setup
from setuptools import find_packages

version = '0.0.1'

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_PATH, "README.md")) as f:
    long_description = f.read()

setup(
    version=version,
    name='certbot-dns-asd',
    description="All Secure Domains DNS API Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tim-seoss/certbot-dns-asd',
    author='Tim Small',
    license='GPL 3.0',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        ],


    packages=find_packages(),
    install_requires=[
        'certbot',
        'zope.interface',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-asd = certbot_dns_asd.dns_asd:Authenticator',
        ],
    },
)
