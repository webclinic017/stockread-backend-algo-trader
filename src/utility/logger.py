import logging.handlers
import os

from .notification import NotificationHandler
from ..config.config import BASE_DIR

LOG_FOLDER_PATH = os.path.join(BASE_DIR, 'logs')


class Logger:
    logger = None
    notification_handler = None

    def __init__(self, logging_service="stock_trading", local=False, console=True, log_folder_path=LOG_FOLDER_PATH,
                 enable_notifications=True):

        # Logger setup
        self.logger = logging.getLogger(f"{logging_service}_logger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.log_folder_path = log_folder_path
        self.enable_notifications = enable_notifications

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # default is "logs/crypto_trading.log"
        if local:
            fh = logging.FileHandler(os.path.join(log_folder_path, f'{logging_service}.log'))
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        # logging to console
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # notification handler
        self.notification_handler = NotificationHandler(self.enable_notifications)

    def log(self, message, level="info", notification=False, notification_tag=None):

        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)

        if notification and self.notification_handler.enabled:
            self.notification_handler.send_notification(str(message), tag=notification_tag)

    def send_notification(self, message: str, tag):
        if self.enable_notifications:
            self.notification_handler.send_notification(message, tag=tag)
        else:
            self.notification_handler.enable_notification()
            self.notification_handler.send_notification(message, tag=tag)
            self.notification_handler.unable_notification()


    def info(self, message, notification=False):
        self.log(message, "info", notification)

    def warning(self, message, notification=False):
        self.log(message, "warning", notification)

    def error(self, message, notification=False):
        self.log(message, "error", notification)

    def debug(self, message, notification=False):
        self.log(message, "debug", notification)

