try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    "description": "Bits of python that I find useful",
    "author": "Richard Futrell",
    "url": "http://web.mit.edu/futrell/www",
    "download_url": "",
    "author_email": "futrell@mit.edu",
    "version": "0.3",
    "install_requires": "nose ".split(),
    "packages": "rfutils ".split(),
    "scripts": "".split(),
    "name": "rfutils",
}

setup(**config)
