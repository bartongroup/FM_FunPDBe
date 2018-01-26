import unittest
from client.funpdbe_client import User


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User("foo", "bar")

    def test_setting_user_name(self):
        self.assertIsNotNone(self.user.user_name)



#
# example_json = {
#     "pdb_id": "1abc",
#     "data_resource": "funsites",
#     "resource_version": "1.0.0",
#     "software_version": "1.0.0",
#     "resource_entry_url": "https://example.com/foo/bar",
#     "release_date": "01/01/2000",
#     "chains": [
#         {
#             "chain_label": "A",
#             "chain_annotation": "foo",
#             "residues": [
#                 {
#                     "pdb_res_label": "1",
#                     "aa_type": "A",
#                     "site_data": [
#                         {
#                             "site_id_ref": 1,
#                             "value": 0.7,
#                             "confidence": 0.9,
#                             "classification": "reliable"
#                         }
#                     ]
#                 }
#             ]
#         }
#     ],
#     "sites": [
#         {
#             "site_id": 1,
#             "label": "ligand_binding_site",
#             "source_database": "pdb",
#             "source_accession": "1ABC",
#             "source_release_date": "01/01/2000"
#         }
#     ],
#     "evidence_code_ontology": [
#         {
#             "eco_term": "manually_curated"
#         }
#     ]
# }


