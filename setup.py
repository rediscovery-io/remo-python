from setuptools import setup, find_packages

setup(
    name='remo-sdk',
    version='0.0.1',
    author='Rediscovery',
    author_email='hello@remo.ai',
    packages=find_packages(exclude=['backup', 'example']),
    url='https://github.com/rediscovery-io/remo-python',
    license='LICENSE.txt',
    description='Remo sdk',
    install_requires=[
        # "certifi==2018.11.29"
        # "chardet==3.0.4"
        # "idna==2.8"
        "Pillow==6.2.0",
        "requests==2.21.0",
        "urllib3==1.24.2",
        "filetype==1.0.5",
        "peewee==3.11.2",
    ],
    classifiers=[
        'Private :: Do Not Upload',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: Creative Commons Attribution-NoDerivatives 4.0 International Public License (CC BY-ND 4.0)'
    ],
    python_requires='>=3.6',
)
