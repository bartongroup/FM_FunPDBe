=====
FunPDBe Deposition Client
=====

This client can be used for depositing functional annotations to the FunPDBe deposition system.

The FunPDBe project is described at: https://funpdbe.org

Quick start
-----------

The client can be used to connect to the FunPDBe deposition system API, and perform GET, POST, PUT and DELETE calls. With the exception of GET calls, all other calls require user authentication (user name and password).
Users (and data resources) can be registered at https://funpdbe.org

Examples of usage:

$ funpdbe_client.py --help

Usage parameters:

-h, --help:       Help (this is what you see now)
-u, --user:       FunPDBe user name
-p, --pwd:        FunPDBe password
-m, --mode:       Running mode (get, post, delete, put)
-i, --pdbid:      PDB id of an entry
-r, --resource:   Name of a resource
-f, --path:       Path to JSON file (.json ending), or files (folder name)
-d, --debug:      Enable more detailed logging

Examples:

1.) Listing all entries
./funpdbe_client.py -user=username -pwd=password --mode=get

2.) Listing entries for PDB id 1abc
./funpdbe_client.py -user=username -pwd=password --mode=get --pdb_id=1abc

3.) Listing entries from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --resource=funsites

4.) Listing entries for PDB id 1abc from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --pdb_id=1abc --resource=funsites

5.) Posting an entry to funsites
./funpdbe_client.py -user=username -pwd=password --mode=post --path=path/to/data.json --resource=funsites

6.) Deleting an entry (1abc) from funsites
./funpdbe_client.py -user=username -pwd=password --mode=delete --pdb_id=1abc --resource=funsites

7.) Updating an entry (1abc) from funsites
./funpdbe_client.py -user=username -pwd=password --mode=put --path=path/to/data.json --resource=funsites --pdb_id=1abc