from setuptools import setup, find_packages

setup(
    name='remo-sdk',
    version='0.0.2',
    author='Rediscovery',
    author_email='hello@remo.ai',
    packages=find_packages(exclude=['backup', 'example']),
    url='https://github.com/rediscovery-io/remo-python',
    license='LICENSE.txt',
    description='Remo sdk',
    install_requires=[
        'filetype>=1.0.5',
        'requests>=2.21.0',
        # 'urllib3==1.24.2',
        # 'Pillow==6.2.0',
        # 'peewee==3.11.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        
        'Operating System :: OS Independent',
    ],
)
