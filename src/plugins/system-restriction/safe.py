#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.logger = self.get_logger()

    def handle_safe_mode(self):
        # TODO Do what do you want to do!
        hibernate_settings_path = "/etc/polkit-1/localauthority/50-local.d/lider.ahenk.enable-hibernate.pkla"
        if self.is_exist(hibernate_settings_path):
            self.delete_file(hibernate_settings_path)
            self.logger.info("System restrictions returned to default settings")
        else:
            self.logger.info("{} File not found".format(hibernate_settings_path))

def handle_mode(context):
    safe = Safe(context)
    safe.handle_safe_mode()
