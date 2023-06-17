import logging


def get_logger(logger_name: str):
    # TODO: Create a config file for log configuration that may allow file logging and also JSON log for monitoring.
    #  The config file may also set specific log levels for each situation.
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return logging.getLogger(logger_name)
