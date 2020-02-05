from setuptools import setup, find_packages

setup(
    name='remo-sdk',
    version='0.0.12',
    author='Rediscovery.io',
    author_email='hello@remo.ai',
    packages=find_packages(exclude=['backup', 'example']),
    url='https://github.com/rediscovery-io/remo-python',
    license='LICENSE.txt',
    description='Remo sdk',
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
        
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
