class Constants(object):
    """
    Constant variables for the deposition client
    """

    def __init__(self):
        self.API_URL = "http://127.0.0.1:8000/funpdbe_deposition/entries/"
        self.RESOURCES = (
            "funsites",
            "3dligandsite",
            "nod",
            "popscomp",
            "14-3-3-pred",
            "dynamine",
            "cansar",
            "credo"
        )
        self.PDB_ID_PATTERN = "[0-9][a-z][a-z0-9]{2}"

    def get_api_url(self):
        return self.API_URL

    def get_resources(self):
        return self.RESOURCES

    def get_pdb_id_pattern(self):
        return self.PDB_ID_PATTERN
