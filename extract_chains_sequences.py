# -*- coding: utf-8 -*-

import os
import sys
import click
import logging
import textwrap
import click_log


from proteofav.variants import fetch_uniprot_pdb_mapping
from proteofav.structures import mmCIF, get_sequence, filter_structures


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--pdb', type=str, default=None,
              help='Protein data bank identifier.')
@click.option('--chain', type=str, default=None,
              help='Protein structure chain identifier.')
@click.option('--uniprot', type=str, default=None,
              help='UniProt KnowledgeBase accession.')
@click.option('-l', '--log', default=sys.stderr,
              help="Path to the logfile.",
              type=click.File('wb'))
@click.argument('input',
                type=click.File('r'), required=False)
@click.argument('output',
                type=click.File('w'), required=False)
@click_log.simple_verbosity_option(default="INFO")
def main(pdb, chain, uniprot, input, output, log):

    logging.basicConfig(stream=log,
                        format='%(asctime)s - %(levelname)s - %(message)s ')

    # process input
    pdbs = []
    chains = []
    if uniprot is not None and not pdb and not chain:
        # get mapped pdb and chains
        r = fetch_uniprot_pdb_mapping(uniprot)
        if r is not None and hasattr(r, 'ok'):
            for i in range(len(r.json()[uniprot])):
                pdb = r.json()[uniprot][i]['pdb_id']
                chain = r.json()[uniprot][i]['chain_id']
                pdbs.append(pdb)
                chains.append(chain)
    elif pdb is not None and chain is not None:
        pdbs = [pdb]
        chains = [chain]
    elif pdb is not None:
        pdbs = [pdb]
    elif input is not None:
        # read file
        lines = input.readlines()
        for line in lines:
            pdb = line.rstrip().lower()
            pdbs.append(pdb)
    else:
        raise ValueError("Either pass a combination of PDB/CHAIN, PDB or UniProt IDs. "
                         "Alternatively, pass a file composed of PDB IDs.")

    # get chains if missing
    if not chains:
        new_pdbs = []
        for pdb in pdbs:
            # get chains
            mmcif_file = os.path.join(os.path.dirname(__file__), 'data', 'input', '{}.cif'.format(pdb))
            mmCIF.download(identifier=pdb, filename=mmcif_file)
            mmcif = mmCIF.read(filename=mmcif_file)
            for chain in mmcif.auth_asym_id.unique():
                chains.append(chain)
                new_pdbs.append(pdb)
        pdbs = new_pdbs

    # get sequence for each PDB/CHAIN
    for pdb, chain in zip(pdbs, chains):
        mmcif_file = os.path.join(os.path.dirname(__file__), 'data', 'input',
                                  '{}.cif'.format(pdb))
        mmCIF.download(identifier=pdb, filename=mmcif_file)
        mmcif = mmCIF.read(filename=mmcif_file)
        mmcif = filter_structures(mmcif, models='first', chains=chain, res=None, res_full=None,
                                  comps=None, atoms=None, lines='ATOM', category='auth',
                                  residue_agg=True, agg_method='first',
                                  add_res_full=True, add_atom_altloc=False, reset_atom_id=True,
                                  remove_altloc=False, remove_hydrogens=False, remove_partial_res=False)
        seq = get_sequence(mmcif)
        seq = '\n'.join(textwrap.wrap(seq, width=60))
        sequence = ">{}_{}\n{}\n".format(pdb, chain, seq)

        if output:
            output.write(sequence)
        else:
            print(sequence)


if __name__ == "__main__":
    main()
