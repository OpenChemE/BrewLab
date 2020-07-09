from setuptools import setup, find_packages

setup(
    name='brewlab',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flake8',
        'autopep8',
        'docutils',
        'pygments',
        'pandas',
        'serial',
        'openpyxl',
        'matplotlib',
        'keyboard',
    ],
)
