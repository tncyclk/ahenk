#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Tucnay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import json
from base.plugin.abstract_plugin import AbstractPlugin


class InstalledApplications(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.temp_file_name = str(self.generate_uuid())
        self.file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)

    def handle_task(self):
        try:
            self.logger.debug('Executing command for package list.')
            self.execute(
                'dpkg-query -f=\'${{Status}},${{binary:Package}}\n\' -W \'*\' | grep \'install ok installed\' | sed \'s/install ok installed/i/\' | sed \'s/unknown ok not-installed/u/\' | sed \'s/deinstall ok config-files/u/\' | grep -v ahenk > {0}'.format(
                    self.file_path))
            self.logger.debug('Command executed.')
            apps = self.db_service.select('app_restriction', '*')
            self.logger.info("Get application from ahenk.db "+str(apps))
            for app in apps:
                self.logger.debug(str(app[1]))
                is_exist = self.is_exist_in_file(app[1])
                if is_exist is True:
                    self.replace_app_in_file(app)

            if self.is_exist(self.file_path):
                data = {}
                md5sum = self.get_md5_file(str(self.file_path))
                self.logger.debug('{0} renaming to {1}'.format(self.temp_file_name, md5sum))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + '/' + md5sum)
                self.logger.debug('Renamed.')
                data['md5'] = md5sum
                json_data = json.dumps(data)

                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Uygulama listesi başarıyla okundu.',
                                             data=json_data,
                                             content_type=self.get_content_type().TEXT_PLAIN.value)

                self.logger.debug('Application list created successfully')
            else:
                raise Exception('File not found on this path: {}'.format(self.file_path))

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Uygulama listesi oluşturulurken hata oluştu: ' + str(e),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


    def is_exist_in_file(self, app_name):
        with open(self.file_path) as f:
            if app_name in f.read():
                return True
            else:
                return False

    def replace_app_in_file(self, app):
        old_line = 'i,{0}'.format(app[1])
        new_line = 'i,{0},{1},{2}'.format(app[1], app[2], app[3])
        file_app = open(self.file_path, 'r')
        file_data = file_app.read()
        file_data = file_data.replace(old_line, new_line)
        file_app.close()

        file_app = open(self.file_path, 'w')
        file_app.write(file_data)
        file_app.close()
        self.logger.info("Replaced successfully restriction application in installed application")

def handle_task(task, context):
    plugin = InstalledApplications(task, context)
    plugin.handle_task()
