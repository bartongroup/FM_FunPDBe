FunPDBe Deposition Client
=====

[![Build Status](https://travis-ci.org/funpdbe-consortium/funpdbe-client.svg?branch=master)](https://travis-ci.org/funpdbe-consortium/funpdbe-client)
[![codecov](https://codecov.io/gh/funpdbe-consortium/funpdbe-client/branch/master/graph/badge.svg)](https://codecov.io/gh/funpdbe-consortium/funpdbe-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/eac066fbf15333153070/maintainability)](https://codeclimate.com/github/funpdbe-consortium/funpdbe-client/maintainability)

The client can be used to connect to the FunPDBe deposition system API, and perform GET, POST, PUT and DELETE calls. With the exception of GET calls, all other calls require user authentication.

<!--- For more information on the FunPDBe initiative, visit https://funpdbe.org --->

Quick start
-----------

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

There are no prerequisites for installing the client.
<!--- There are no prerequisites for installing the client, but in order to connect to the FunPDBe deposition system using this client, depositors have to register an account at https://funpdbe.org/register. Activating user accounts in dependent on admin approval. --->

### Installing

The are two main approaches to getting the client up and running.

#### Checking out this repository

```
$ git clone https://github.com/funpdbe-consortium/funpdbe-client
$ cd funpdbe-client
$ pip install -r requirements.txt
```

## Usage

Examples of usage:

```
$ ./funpdbe_client.py
```

### Parameters

* -h, --help:       Help (this is what you see now)
* -u, --user:       FunPDBe user name
* -p, --pwd:        FunPDBe password
* -m, --mode:       Running mode (get, post, delete, put, validate)
* -i, --pdbid:      PDB id of an entry
* -r, --resource:   Name of a resource
* -f, --path:       Path to JSON file (.json ending), or files (folder name)
* -d, --debug:      Enable more detailed logging

### Examples

#### Validating JSON file against schema
```
$ ./funpdbe_client.py --path=path/to/file.json --mode=validate
```

#### Listing all entries
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=get
```

#### Listing entries for PDB id 1abc
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=get --pdb_id=1abc
```

#### Listing entries from funsites
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=get --resource=funsites
```

#### Listing entry for PDB id 1abc from funsites
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=get --pdb_id=1abc --resource=funsites
```

#### Posting an entry to funsites
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=post --path=path/to/data.json --resource=funsites
```

#### Deleting an entry (1abc) from funsites
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=delete --pdb_id=1abc --resource=funsites
```

#### Updating an entry (1abc) from funsites
```
$ ./funpdbe_client.py --user=username --pwd=password --mode=put --path=path/to/data.json --resource=funsites --pdb_id=1abc
```

## Running the tests

Running tests for the client is performed simply by using
```
$ pytest
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/funpdbe-consortium/funpdbe-client/tags).

## Authors

* **Mihaly Varadi** - *Initial work* - [mvaradi](https://github.com/mvaradi)

See also the list of [contributors](https://github.com/funpdbe-consortium/funpdbe-client/graphs/contributors) who participated in this project.

## License

This project is licensed under the EMBL-EBI License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

We would like to thank the PDBe team for their support and feedback, as well as all the members of the FunPDBe consortium:

* PDBe team - [team website](https://www.ebi.ac.uk/services/teams/pdbe)
* Orengo team - [CATH](http://www.cathdb.info/)
* Vranken team - [DynaMine](http://dynamine.ibsquare.be/)
* Barton team - [NoD](http://www.compbio.dundee.ac.uk/www-nod/)
* Wass team - [3DLigandSite](http://www.sbg.bio.ic.ac.uk/3dligandsite/)
* Blundell team - [CREDO](http://marid.bioc.cam.ac.uk/credo)
* Fraternali team - [POPSCOMP](https://mathbio.crick.ac.uk/wiki/POPSCOMP)
