#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json

class Sample(AbstractPlugin):
    def __init__(self, profile_data, context):
        super(Sample, self).__init__()
        self.profile_data = profile_data
        self.context = context
        self.message_code = self.get_message_code()
        self.logger = self.get_logger()
        self.parameters = json.loads(self.profile_data)

    def handle_policy(self):
        # TODO Do what do you want to do!
        # TODO Don't Forget returning response with <self.context.create_response(..)>
        try:
            username = self.context.get('username')
            self.logger.debug('Permissions will be applied for profile')
            if self.has_attr_json(self.parameters, 'hibernate') is True:
                hibernate = self.parameters['hibernate']
                self.settings_hibernate(hibernate, username)

            else:
                self.logger.debug('Data has no parameter "hibernate"')

            self.logger.info('System restriction profile is handled successfully.')
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='Sistem kısıtlamaları politikası başarıyla güncellendi.')

        except Exception as e:
            self.logger.error('A problem occurred while handling USB policy. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='Sistem kısıtlamaları politikası uygulanırken bir hata oluştu: {0}'.format(str(e)))

    def settings_hibernate(self, hibernate_data, username):

        temp_hibernate = "[Re-enable hibernate by default for login1]\n" \
                         "  Identity=unix-user:{1}\n" \
                         "  Action=org.freedesktop.login1.hibernate\n" \
                         "  ResultActive={0}\n" \
                         "[Re-enable hibernate for multiple users by default in logind]\n" \
                         "  Identity=unix-user:{1}\n" \
                         "  Action=org.freedesktop.login1.hibernate-multiple-sessions\n" \
                         "  ResultActive={0}"

        # close hibernate if data is active
        privilege = None
        if hibernate_data == "1":
            privilege = "yes"
        # open hibernate if data is active
        elif hibernate_data == "0":
            privilege = "no"
        hibernate_settings_path = "/etc/polkit-1/localauthority/50-local.d/lider.ahenk.enable-hibernate.pkla"
        if not self.is_exist(hibernate_settings_path):
            self.logger.info("lider-ahenk.enable-hibernate.pkla does not exist.")
            self.create_file(hibernate_settings_path)
            self.write_file(hibernate_settings_path, temp_hibernate.format(privilege, username))
            self.logger.info("Create file and write hibernate data to {0} file ".format(hibernate_settings_path))
            self.logger.info("Enabled hibernate settings successfully")

        else:
            self.logger.info("{} file already exists".format(hibernate_settings_path))


def handle_policy(profile_data, context):
    print('Sample Plugin Policy')
    sample = Sample(profile_data, context)
    sample.handle_policy()
