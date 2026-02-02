import logging


class BotLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, error_message):
        self.logger.error(error_message)
