import logging
from funpdbe_client.constants import LOG_FILENAME


class FunPDBeClientLogger(object):

    def __init__(self, name="general"):
        self.logger = logging.getLogger(name)
        self.configure()

    def configure(self):
        config = logging.FileHandler(LOG_FILENAME)
        config.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        config.setFormatter(formatter)
        self.logger.addHandler(config)

    def log(self):
        return self.logger