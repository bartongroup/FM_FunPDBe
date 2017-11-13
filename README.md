# FM_FunPDBe
Scripts for adding functional annotations to FunPDBe.


## How to use

### Getting Fasta sequences from a list of PDB ids

Extracting the sequences from all chains in the PDB files
```sh
$ python extract_sequences.py data/funpdbe_examples_list.txt data/funpdbe_examples_list.fasta 
```

### Getting Fasta sequences from PDB/CHAIN or UniProt IDs

Extracting the sequence from all chains based on a PDB ID
```sh
$ python extract_sequences.py --pdb <pdb_id> 
```

Extracting the sequence from all chains based on a PDB ID and Chain ID
```sh
$ python extract_sequences.py --pdb <pdb_id> --chain <chain_id>
```

Extracting the sequence from all PDB/Chain IDs based on a UniProt ID
```sh
$ python extract_sequences.py --uniprot <pdb_id>
```

### Running Barton Group Predictors on a collection of Fasta sequences

Running NOD
```sh
$ python run_predictors.py nod data/funpdbe_examples_list.fasta
```

Running 14-3-3-Pred
```sh
$ python run_predictors.py 1433pred data/funpdbe_examples_list.fasta
```

Running Jpred
```sh
$ python run_predictors.py jpred data/funpdbe_examples_list.fasta
```


## Scoring and Classifier Thresholds

**NOD**  
* NOD - Artificial Neural Network (20-length sequence windows with a score cut-off >= 0.8)

**14-3-3-Pred**  
* ANN - Artificial Neural Network (cut-off >= 0.55)
* PSSM - Position-Specific Scoring Matrix (cut-off >= 0.80)
* SVM - Support Vector Machine (cut-off >= 0.25)
* Consensus - Average of the scores provided by the three methods (cut-off >= 0.50)


## Dependencies
Using Python 3.5+. Check [requirements.txt](./requirements.txt) for all Python dependencies.

Other Dependencies:
* NOD requires **batchman** from SNNS package to be installed. See http://www.compbio.dundee.ac.uk/www-nod/downloads.jsp for more details.
* 14-3-3-Pred requires **PyML**. See http://pyml.sourceforge.net/index.html for more on how to install it.