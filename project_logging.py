import logging
import newegg_crawl_config as config

log_level = config.log_level

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

if (config.log_to_file):
    fh = logging.FileHandler(config.log_file)
    fh.setLevel(log_level)

ch = logging.StreamHandler()
ch.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

