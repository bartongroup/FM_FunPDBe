from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='funpdbe-client',
    version='0.1.0',
    description='Deposition client for FunPDBe',
    long_description=readme,
    author='Mihaly Varadi',
    author_email='mvaradi@ebi.ac.uk',
    url='https://github.com/mvaradi/funpdbe-client',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)