import functools
import json
import jsonmerge
import os
import schema


from pprint import pprint
from proteofav.structures import mmCIF, get_sequence, filter_structures
from time import localtime


def read_mmcif_chain(pdb, chain):
    mmcif_file = os.path.join(os.path.dirname(__file__), 'data', 'input',
                              '{}.cif'.format(pdb))
    if not os.path.exists(mmcif_file):
        mmCIF.download(identifier=pdb, filename=mmcif_file)
    mmcif = mmCIF.read(filename=mmcif_file)
    mmcif = filter_structures(mmcif, models='first', chains=chain, res=None, res_full=None,
                              comps=None, atoms=None, lines='ATOM', category='auth',
                              residue_agg=True, agg_method='first',
                              add_res_full=True, add_atom_altloc=False, reset_atom_id=True,
                              remove_altloc=False, remove_hydrogens=False, remove_partial_res=False)
    return mmcif


def format_1433_site(site, mmcif_table):
    """

    :param site:
    :param mmcif:
    :return:
    """

    def parse_site_to_FunPDBe_chain_json(site, mmcif_series, cutoffs):
        # Get fields needed for FunPDBe schema: NB. how do we differentiate positive vs negative predictions
        # There will be redundency if we include the flanking residues in the site, since they all have the same score.
        # Perhaps we could use 'additional_site_annotations'...
        # Should normalise negative and positive predictions for min:cutoff and cutoff:max
        # Should confidence account for pSer/Thr too?
        predicted_1433 = float(site['Consensus']) > cutoffs['Consensus']
        additional_residue_annotations = {
            'pSer/Thr': site['pSer/Thr'],
            'Concordance': [method for method in ['SVM', 'ANN', 'PSSM'] if float(site[method]) > cutoffs[method]],
            'Prediction': '14-3-3 Binding' if predicted_1433 else 'Not candidate site'
        }
        additional_residue_annotations.update({k: float(v) for k, v in site.items() if k in ['SVM', 'ANN', 'PSSM']})
        d = {
            "chains": [
                {
                    "chain_id": mmcif_series['label_asym_id'],
                    "additional_chain_annotations": {},
                    "residues": [
                        {
                            "pdb_res_label": mmcif_series['pdbe_label_seq_id'],  # Make sure is str
                            "aa_type": mmcif_series['label_comp_id'],
                            "additional_residue_annotations": additional_residue_annotations,
                            "site_data": [
                                {
                                    "site_id_ref": site['Site'],  # or increment from 1...
                                    "value": float(site['Consensus']),
                                    "confidence": 1 if predicted_1433 else 0,  # TODO: will get model ranges and can make 0-1
                                    "classification": 'reliable',  # TODO: Make this reflect confidence in some way
                                }
                            ]
                        }
                    ]
                }
            ],
        }
        return d, predicted_1433
    
    cutoffs = {'Consensus': 0.50, 'SVM': 0.25, 'PSSM': 0.80, 'ANN': 0.55}

    # Lookup site in mmcif and verify amino acids match
    site_mmcif_index = site['Site'] - 1
    site_mmcif_start, site_mmcif_end = (0 if site_mmcif_index < 6 else site_mmcif_index - 6, site_mmcif_index + 4)
    site_mmcif = mmcif_table.iloc[site_mmcif_start:site_mmcif_end+1]
    site_mmcif_seq = get_sequence(site_mmcif)
    seq = site['Peptide'].replace('-', '').upper()  # Drop gaps
    assert seq == site_mmcif_seq

    # Format site and mmcif data to FunPDBe; for the moment only the S/T
    mmcif_series = mmcif_table.iloc[site_mmcif_index]
    d, predicted_1433 = parse_site_to_FunPDBe_chain_json(site, mmcif_series, cutoffs)


    # Add 'site' level annotation
    d.update({
        "sites": [
            {
                "site_id": site['Site'],  # or increment from 1...
                "label_id_ref": 1 if predicted_1433 else 2,
                "evidence": {
                    "source_id_ref": 1,  # TODO: Not meaningful just now
                    "source_accession": ""
                }
            }
        ]
    })

    return d


if __name__ == '__main__':
    # Load mmcif and corresponding predictions
    mmcif = read_mmcif_chain('3tpp', 'A')
    prediction_result_file = './data/output/1433pred/3tpp_A.json'
    one433_sites = json.load(open(prediction_result_file))

    # Create FunPDBe JSONs for each prediction
    sites_jsons = [format_1433_site(site, mmcif) for site in one433_sites]

    # Merge FunPDBe JSONs respecting schema
    merged_sites_json = functools.reduce(schema.FunPDBe_merger.merge, sites_jsons)

    # Fill top level FunPDBe JSON fields:
    top_level_json = schema.resource_header('14-3-3 Pred', software_version='76237a4cc452d99a0df68ffff41c520b33c86fee',
                                            resource_entry_url='http://www.compbio.dundee.ac.uk/1433pred/')
    top_level_json.update(pdb_id='3tpp')
    top_level_json.update(chains=[{'chain_id': 'A', 'additional_chain_annotations': {}, 'residues': []}])

    # Release date
    struct_time = localtime(os.path.getmtime(prediction_result_file))
    date_string = '/'.join([str(getattr(struct_time, attr)) for attr in ('tm_mday', 'tm_mon', 'tm_year')])
    top_level_json.update(release_date=date_string)

    # 'labels' (referenced to 'sites')
    top_level_json.update(labels=[{'label_id': 1, 'label_text': '14-3-3 Binding'},
                                  {'label_id': 2, 'label_text': 'Negative prediction'}])

    # Other
    top_level_json.update(additional_entry_annotations={}, evidence_code_ontology=['...'], source_datasets=[], sites=[])

    # Merge site and top level annotations
    FunPDBe_json = schema.FunPDBe_merger.merge(top_level_json, merged_sites_json)

    schema.validate_FunPDBe_entry(FunPDBe_json)
    with open('14_3_3_Pred.json', 'w') as output:
        json.dump(FunPDBe_json, output, indent=4, sort_keys=True)
    pprint(FunPDBe_json)

