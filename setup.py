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
)
