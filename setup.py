from setuptools import setup, find_packages
from codecs import open
from os import path
import ssiwebd

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'ssiwebd',
    version = ssiwebd.__version__,
    description = 'Server Side Include Webd',
    long_description=long_description,
    author = 'Solomon Huang',
    author_email = 'kaichan@gmail.com',
    url = 'https://github.com/solomonhuang/ssiwebd',
    license='BSD',
    keywords = 'ssi webd',
    packages=find_packages(exclude=['dist']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points = {
        'console_scripts': [
            'ssiwebd=ssiwebd:main',
        ],
    },
)
