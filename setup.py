from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='funpdbe_client',
    version='1.0.0',
    description='Deposition client for FunPDBe',
    long_description=readme,
    author='Mihaly Varadi',
    author_email='mvaradi@ebi.ac.uk',
    url='https://github.com/funpdbe-consortium/funpdbe-client',
    license=license,
    packages=['funpdbe_client'],
    install_requires=[
        'jsonschema'
    ]
)