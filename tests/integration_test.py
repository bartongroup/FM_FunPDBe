import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client.funpdbe_client import *

def integration_test():
    """
    Integration test of all the calls
    :return: Boolean
    """
    # Test user
    c = Client("test", "asdasd42")
    # Mock data
    c.json_data = {
         "pdb_id": "0x00",
         "data_resource": "funsites",
         "resource_version": "1.0.0",
         "software_version": "1.0.0",
         "resource_entry_url": "https://example.com/foo/bar",
         "release_date": "01/01/2000",
         "chains": [
             {
                 "chain_label": "A",
                 "chain_annotation": "foo",
                 "residues": [
                     {
                         "pdb_res_label": "1",
                         "aa_type": "ALA",
                         "site_data": [
                             {
                                 "site_id_ref": 1,
                                 "raw_score": 0.7,
                                 "confidence_score": 0.9,
                                 "confidence_classification": "high"
                             }
                         ]
                     }
                 ]
             }
         ],
         "sites": [
             {
                 "site_id": 1,
                 "label": "ligand_binding_site",
                 "source_database": "pdb",
                 "source_accession": "1abc",
                 "source_release_date": "01/01/2000"
             }
         ],
         "evidence_code_ontology": [
             {
                 "eco_term": "manually_curated",
                 "eco_code": "ECO000042"
             }
         ]
    }
    # Test POST when entry does not exist
    post_new = c.post()
    if post_new.status_code == 201:
        logging.info("PASS: POSTed successfully")
    else:
        logging.error("FAIL: POST failed")
        return False
    # Test POST when entry is already there
    post_again = c.post()
    if post_again.status_code == 400:
        logging.info("PASS: cannot POST the same thing twice")
    else:
        logging.error("FAIL: should not be able to POST twice")
        return False
    # Test POST when data is bad
    c.json_data = ""
    bad_post = c.post()
    if bad_post.status_code == 400:
        logging.info("PASS: bad JSON caught")
    else:
        logging.error("FAIL: bad data went through")
    # Test GET all
    get_all = c.get_all()
    if get_all.status_code == 200:
        logging.info("PASS: GET all entries worked")
    else:
        logging.error("FAIL: GET all entries failed")
        return False
    # Test GET one by PDB id
    get_one_pdb = c.get_one("0x00")
    if get_one_pdb.status_code == 200:
        logging.info("PASS: GET one by PDB id worked")
    else:
        logging.error("FAIL: GET one by PDB id failed")
        return False
    # Test GET one by PDB id not existing
    get_one_pdb_none = c.get_one("invalid")
    if get_one_pdb_none.status_code == 404:
        logging.info("PASS: GET failed for non existing entry")
    else:
        logging.error("FAIL: should not GET what is not there")
        return False
    # Test GET all by resource
    get_all_resource = c.get_all("funsites")
    if get_all_resource.status_code == 200:
        logging.info("PASS: GET all for resource worked")
    else:
        logging.error("FAIL: GET all for resource failed")
        return False
    # Test GET all by invalid resource
    get_all_resource_none = c.get_all("invalid")
    if get_all_resource_none.status_code == 400:
        logging.info("PASS: GET all for resource failed for bad resource")
    else:
        logging.error("FAIL: GET all for resource worked for bad resource")
        return False
    # Test GET one by PDB and resource
    get_one_res_pdb = c.get_one("0x00", "funsites")
    if get_one_res_pdb.status_code == 200:
        logging.info("PASS: GET one by PDB id and resource worked")
    else:
        logging.error("FAIL: GET one by PDB id and resource failed")
        return False
    # Test GET one by bad PDB or bad resource
    get_one_res_pdb_bad = c.get_one("foo", "bar")
    if get_one_res_pdb_bad.status_code == 404:
        logging.info("PASS: GET one by PDB id and resource failed for bad data")
    else:
        logging.error("FAIL: GET one by PDB id and resource worked for bad data")
        return False
    # Test DELETE when not authorized
    c.user.user_name = "test2"
    unauthorized_delete = c.delete_one("0x00")
    if unauthorized_delete.status_code == 404:
        logging.info("PASS: could not DELETE other user data")
    else:
        logging.critical("FAIL: could DELETE other user data")
        return False
    # Test DELETE when entry is there
    c.user.user_name = "test"
    delete_entry = c.delete_one("0x00")
    if delete_entry.status_code == 200:
        logging.info("PASS: could DELETE")
    else:
        logging.error("FAIL: failed to DELETE")
        return False
    # Test DELETE when entry is not there
    delete_again = c.delete_one("0x00")
    if delete_again.status_code == 404:
        logging.info("PASS: cannot delete entry twice")
    else:
        logging.error("FAIL: should not be able to DELETE twice")
        return False

    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger(__name__)
    if integration_test():
        print("Passed all tests")
    else:
        print("Some tests failed")