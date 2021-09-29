import os
from os import path

import apprise

from src.config.config import BASE_DIR

apprise_config_path = os.path.join(BASE_DIR, 'config', 'apprise.yml')


class NotificationHandler:
    def __init__(self, enabled=True):
        if enabled and path.exists(apprise_config_path):
            self.apobj = apprise.Apprise()
            config = apprise.AppriseConfig()
            config.add(apprise_config_path)
            self.apobj.add(config)

            self.enabled = True
        else:
            self.enabled = False

    def enable_notification(self):
        self.enabled = True

    def unable_notification(self):
        self.enabled = False

    def send_notification(self, message, tag, title=None):
        if self.enabled:
            if title:
                self.apobj.notify(body=message, title=title, tag=tag)
            else:
                self.apobj.notify(body=message, tag=tag)


if __name__ == '__main__':
    is_test_run = True

    if is_test_run:
        nh = NotificationHandler()
        nh.send_notification('Signal', tag="signal")
        nh.send_notification('Order', tag="order")

    else:
        pass

