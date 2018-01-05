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


def prepare_chain_entry(chain_id, pdb_res_label, aa_type, site_id_ref, value, confidence, classification,
                        additional_chain_annotations={}, additional_residue_annotations={},
                        additional_site_data_annotations={}):
    """
    Create a FunPDBe formatted chain/residue/site_data entry.

    :param chain_id:
    :param pdb_res_label:
    :param aa_type:
    :param site_id_ref:
    :param value:
    :param confidence:
    :param classification:
    :param additional_chain_annotations:
    :param additional_residue_annotations:
    :param additional_site_data_annotations:
    :return:
    """
    d = {
        "chains": [
            {
                "chain_id": chain_id,
                "additional_chain_annotations": additional_chain_annotations,
                "residues": [
                    {
                        "pdb_res_label": pdb_res_label,  # Make sure is str
                        "aa_type": aa_type,
                        "additional_residue_annotations": additional_residue_annotations,
                        "site_data": [
                            {
                                "site_id_ref": site_id_ref,
                                "value": value,
                                "confidence": confidence,
                                "classification": classification,
                                "additional_site_data_annotations": additional_site_data_annotations
                            }
                        ]
                    }
                ]
            }
        ],
    }
    return d


def create_site_json(site_id, label_id_ref, source_id_ref, additional_site_annotations={}):
    """
    Create a FunPDBe site entry.

    :param site_id:
    :param label_id_ref:
    :param source_id_ref:
    :param additional_site_annotations:
    :return:
    """
    sites_component = {
        "sites": [
            {
                "site_id": site_id,
                "label_id_ref": label_id_ref,
                "evidence": {
                    "source_id_ref": source_id_ref,
                    "source_accession": ""
                },
                "additional_site_annotations": additional_site_annotations
            }
        ]
    }
    return sites_component


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
        chain_id = mmcif_series['label_asym_id']
        pdb_res_label = mmcif_series['pdbe_label_seq_id']
        aa_type = mmcif_series['label_comp_id']
        site_id_ref = site_mmcif_index  # or increment from 1...
        value = float(site['Consensus'])
        confidence = 1 if predicted_1433 else 0  # TODO: will get model ranges and can make 0-1
        classification = 'reliable'  # TODO: Make this reflect confidence in some way
        additional_residue_annotations = {}
        if site_mmcif_index == mmcif_index:  # Add phosphorylation status for S/T
            additional_residue_annotations.update({"pSer/Thr": site['pSer/Thr']})
        additional_site_data_annotations = {'motif_position': mmcif_index - site_mmcif_index}
        d = prepare_chain_entry(chain_id, pdb_res_label, aa_type, site_id_ref, value, confidence, classification,
                                additional_residue_annotations=additional_residue_annotations,
                                additional_site_data_annotations=additional_site_data_annotations)
        return d, predicted_1433

    cutoffs = {'Consensus': 0.50, 'SVM': 0.25, 'PSSM': 0.80, 'ANN': 0.55}
    min_max = {'ANN': [0, 1], 'SVM': [-1, 1]}

    # Lookup site in mmcif and verify amino acids match
    site_mmcif_index = site['Site'] - 1
    site_mmcif_start, site_mmcif_end = (0 if site_mmcif_index < 6 else site_mmcif_index - 6, site_mmcif_index + 4)
    site_mmcif = mmcif_table.iloc[site_mmcif_start:site_mmcif_end+1]
    site_mmcif_seq = get_sequence(site_mmcif)
    seq = site['Peptide'].replace('-', '').upper()  # Drop gaps
    assert seq == site_mmcif_seq

    residue_entries = []
    for mmcif_index in range(site_mmcif_start, site_mmcif_end+1):
        # Format site and mmcif data to FunPDBe; for the moment only the S/T
        mmcif_series = mmcif_table.iloc[mmcif_index]
        d, predicted_1433 = parse_site_to_FunPDBe_chain_json(site, mmcif_series, cutoffs)
        residue_entries.append(d)

    # Merge chain level JSONs respecting FunPDBe schema
    d = functools.reduce(schema.FunPDBe_merger.merge, residue_entries)

    # Add 'site' level annotation
    additional_site_annotations = {
        'pSer/Thr': site['pSer/Thr'],
        'concordance': [method for method in ['SVM', 'ANN', 'PSSM'] if float(site[method]) > cutoffs[method]],
        'prediction': '14-3-3 protein_binding_site' if predicted_1433 else 'not_candidate_site',
    }
    additional_site_annotations.update({k: float(v) for k, v in site.items() if k in ['SVM', 'ANN', 'PSSM']})
    label_id_ref = 1 if predicted_1433 else 2
    site_id = site_mmcif_index  # or increment from 1...
    source_id_ref = 1  # TODO: Not meaningful just now
    sites_component = create_site_json(site_id, label_id_ref, source_id_ref, additional_site_annotations)
    d.update(sites_component)

    return d


def format_1433_pdb(source_mmcif, prediction_result_file):
    """

    :param source_mmcif:
    :param prediction_result_file:
    :return:
    """
    # Load predictions
    one433_sites = json.load(open(prediction_result_file))
    # Create FunPDBe JSONs for each prediction
    sites_jsons = [format_1433_site(site, source_mmcif) for site in one433_sites]
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
    top_level_json.update(labels=[{'label_id': 1, 'label_text': '14-3-3 protein_binding_site'},
                                  {'label_id': 2, 'label_text': 'negative_prediction'}])
    # Other
    source_datasets = [
        {
            "source_id": 1,
            "source_release_date": "10/2017",
            "source_db": "PDB"
        },
        {
            "source_id": 2,
            "source_release_date": "10/2013",
            "source_db": "PhosphoSitePlus"
        },
        {
            "source_id": 3,
            "source_release_date": "2014",
            "source_db": "ANIA",
            "source_url": "https://ania-1433.lifesci.dundee.ac.uk/prediction/webserver/index.py",
            "source_publication_doi": "10.1093/database/bat085"
        },
        {
            "source_id": 4,
            "source_release_date": "2015",
            "source_db": "14-3-3 Pred Dataset",
            "source_publication_doi": "10.1093/bioinformatics/btv133"
        }

    ]
    eco_terms = ["sequence_similarity_evidence_used_in_automatic_assertion"]
    top_level_json.update(additional_entry_annotations={}, evidence_code_ontology=eco_terms,
                          source_datasets=source_datasets, sites=[])
    # Merge site and top level annotations
    FunPDBe_json = schema.FunPDBe_merger.merge(top_level_json, merged_sites_json)
    return FunPDBe_json


def parse_nod_results(source_mmcif, prediction_results_file):

    def parse_segment_to_FunPDBe_chain_json(site_id_ref, value,  mmcif_series):
        chain_id = mmcif_series['label_asym_id']
        pdb_res_label = mmcif_series['pdbe_label_seq_id']
        aa_type = mmcif_series['label_comp_id']
        confidence = 1
        classification = 'reliable'  # TODO: Make this reflect confidence in some way
        d = prepare_chain_entry(chain_id, pdb_res_label, aa_type, site_id_ref, value, confidence, classification)
        return d

    # parse NOD results file
    with open(prediction_results_file) as results:
        nods_sections = ['scores', 'segments', 'positions', 'number', 'sequence', 'fasta_header']
        fasta_lines = []
        nols_residue_scores = []
        for line in results:
            line = line.strip()
            # Sequence
            if nods_sections[-1] == 'fasta_header' and line.startswith('>'):
                fasta_lines.append(line)
                nods_sections.pop()
            elif nods_sections[-1] == 'sequence' and line[:1].isalpha() and not line.startswith('NOLS_segment_number'):
                fasta_lines.append(line)
            # Number
            elif nods_sections[-1] == 'sequence' and line.startswith('NOLS_segment_number'):
                nods_sections.pop()
            # elif nods_sections[-1] == 'number' and line.startswith('NOLS_segment_number'):
                n_nols_seqments = int(line.split(' ')[-1])
                nods_sections.pop()
            # Positions
            elif nods_sections[-1] == 'positions' and line.startswith('NOLS_segments_positions'):
                nols_site_ranges = ''.join(line.split(' ')[1:]).split(',')
                nods_sections.pop()
            # Segments
            elif nods_sections[-1] == 'segments' and line.startswith('NOLS_segments'):
                nols_segments = ''.join(line.split(' ')[1:]).split(',')
                nods_sections.pop()
            elif nods_sections[-1] == 'scores' and line[:1] in ['0', '1']:
                nols_residue_scores.append(float(line))
            elif line == '':
                continue
            else:
                raise ValueError('Could not parse NOD results file.')

    # Process NOLS sites
    for site_id, (site_range, site_sequence) in enumerate(zip(nols_site_ranges, nols_segments)):
        start, end = [int(x) for x in site_range.split('-')]
        site_mmcif_start, site_mmcif_end = start-1, end-1
        site_mmcif = source_mmcif.iloc[site_mmcif_start:site_mmcif_end+1]
        site_mmcif_seq = get_sequence(site_mmcif)
        assert site_sequence == site_mmcif_seq

        # Add residue entries
        residue_entries = []
        for mmcif_index in range(site_mmcif_start, site_mmcif_end + 1):
            # Format site and mmcif data to FunPDBe
            mmcif_series = source_mmcif.iloc[mmcif_index]
            d = parse_segment_to_FunPDBe_chain_json(site_id, 1, mmcif_series)
            residue_entries.append(d)

        # Merge chain level JSONs respecting FunPDBe schema
        d = functools.reduce(schema.FunPDBe_merger.merge, residue_entries)

        # Add 'site' level annotation
        label_id_ref = 1
        source_id_ref = 1  # TODO: Not meaningful just now
        additional_site_annotations = {
            'segment': site_sequence,
        }
        sites_component = create_site_json(site_id, label_id_ref, source_id_ref, additional_site_annotations)
        d = schema.FunPDBe_merger.merge(d, sites_component)

    return d


if __name__ == '__main__':
    # Format 1433 example
    mmcif = read_mmcif_chain('3tpp', 'A')
    one433_result_file = './data/output/1433pred/3tpp_A.json'
    FunPDBe_1433_json = format_1433_pdb(mmcif, one433_result_file)

    # Validate and save 1433 example
    schema.validate_FunPDBe_entry(FunPDBe_1433_json)
    with open('14_3_3_Pred.json', 'w') as output:
        json.dump(FunPDBe_1433_json, output, indent=4, sort_keys=True)
    pprint(FunPDBe_1433_json)

