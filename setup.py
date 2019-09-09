from setuptools import setup
from setuptools import find_packages

version = '0.0.1'

setup(
    version=version,
    name='certbot-asd',
    description="All Secure Domains DNS API Authenticator plugin for Certbot",
    packages=find_packages(),
    install_requires=[
        'certbot',
        'zope.interface',
    ],
    entry_points={
        'certbot.plugins': [
            'dns = certbot_asd.dns:Authenticator',
        ],
    },
)
