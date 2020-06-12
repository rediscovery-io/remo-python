from setuptools import setup, find_packages
from remo import __version__

setup(
    name='remo-python',
    version=__version__,
    author='Rediscovery.io',
    author_email='hello@remo.ai',
    packages=find_packages(exclude=['examples']),
    url='https://github.com/rediscovery-io/remo-python',
    license='LICENSE.txt',
    description='Remo python library',
    install_requires=[
        'filetype>=1.0.5',
        'requests>=2.21.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
