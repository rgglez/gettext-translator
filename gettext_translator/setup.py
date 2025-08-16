"""
Setup script for the gettext-translator package.
This script is used to install the package and its dependencies.
"""

from setuptools import find_packages, setup

from gettext_translator.src.version import __version__

# Read the contents of README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gettext-translator',
    version=__version__,
    author='Rodolfo Gonzalez',
    author_email='rodolfo.gonzalez@gmail.com',
    description='A CLI tool for translating .po files using cloud services and/or AI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rgglez/gettext-translator',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'polib',
        'openai',
        'python-dotenv',
        'pytest',
        'rich',
        'requests',
        # Add other dependencies from requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'gettext-translator=gettext_translator.translator:main',
        ],
    },
    classifiers=[
        # Choose your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        # Add additional classifiers as needed
    ],
)
