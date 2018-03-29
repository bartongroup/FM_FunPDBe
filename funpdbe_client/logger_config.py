import logging
from funpdbe_client.constants import LOG_FILENAME


class FunPDBeClientLogger(object):

    def __init__(self, name="general", write_mode="a"):
        self.write_mode = write_mode
        self.logger = logging.getLogger(name)
        self.configure()

    def configure(self):
        config = logging.FileHandler(LOG_FILENAME, mode=self.write_mode)
        config.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        config.setFormatter(formatter)
        self.logger.addHandler(config)
        self.logger.setLevel("INFO")

    def log(self):
        return self.logger

def generic_error():
    print("FAILED - check %s for details" % LOG_FILENAME)