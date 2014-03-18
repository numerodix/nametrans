from setuptools import find_packages
from setuptools import setup

import nametrans


setup(
    name='nametrans',
    version=nametrans.__version__,
    description='Rename files with regex search/replace semantics',
    author='Martin Matusiak',
    author_email='numerodix@gmail.com',
    url='https://github.com/numerodix/nametrans',

    packages=find_packages('.'),
    package_dir={'': '.'},

    install_requires=[
        'ansicolor',
    ],

    entry_points={
        "console_scripts": [
            "nametrans = nametrans.main:main",
        ]
    },

    # don't install as zipped egg
    zip_safe=False,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
