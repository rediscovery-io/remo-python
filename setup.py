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
        'Pillow==6.2.0',
        'requests==2.21.0',
        'urllib3==1.24.2',
        'filetype==1.0.5',
        'peewee==3.11.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: Creative Commons Attribution-NoDerivatives 4.0 International Public License (CC BY-ND 4.0)'
        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        
        'Operating System :: OS Independent',
    ],
)
