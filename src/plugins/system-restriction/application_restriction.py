#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.content_type import ContentType

class DesktopSettings(AbstractPlugin):

    def __init__(self, task, context):
        super(DesktopSettings, self).__init__()
        self.message_code = self.get_message_code()
        self.context = context
        self.task = task
        self.logger = self.get_logger()

        if self.has_attr_json(task, 'hibernate') is True:
            self.hibernate = self.task['hibernate']

        if self.has_attr_json(task, 'app_right_click') is True:
            self.app_right_click = self.task['app_right_click']

        if self.has_attr_json(task, 'desktop_settings') is True:
            self.desktop_settings = self.task['desktop_settings']

        if self.has_attr_json(task, 'panel_preferences') is True:
            self.panel_preferences = self.task['panel_preferences']


    def handle_task(self):
        # TODO Do what do you want to do!
        # TODO Don't Forget returning response with <self.context.create_response(..)>

        try:
            if self.has_attr_json(self.task, 'hibernate') is True:
                self.settings_hibernate(self.hibernate)

            if self.has_attr_json(self.task, 'app_right_click') is True:
                pass

            if self.has_attr_json(self.task, 'desktop_settings') is True:
                pass

            if self.has_attr_json(self.task, 'panel_preferences') is True:
                pass

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                     message='Sistem Kısıtlamaları görevi başarıyla gerçekleştirildi',
                                     content_type=ContentType.APPLICATION_JSON.value)
        except Exception as e:
            self.context.create_response(code=self.message_code.TASK_PROCESSED.TASK_ERROR.value,
                                         message='Sistem Kısıtlamaları görevi çalıştırılırken hata oluştu '+str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)

    def settings_hibernate(self, hibernate_data):

        temp_hibernate = "[Re-enable hibernate by default for login1]\n" \
                         "  Identity=unix-user:*\n" \
                         "  Action=org.freedesktop.login1.hibernate\n" \
                         "  ResultActive={0}\n" \
                         "[Re-enable hibernate for multiple users by default in logind]\n" \
                         "  Identity=unix-user:*\n" \
                         "  Action=org.freedesktop.login1.hibernate-multiple-sessions\n" \
                         "  ResultActive={0}"

        self.logger.info("--->>>> get data: "+str(hibernate_data))
        # close hibernate if data is active
        if hibernate_data == "active":
            a = "yes"
        # open hibernate if data is active
        elif hibernate_data == "passive":
            a = "no"

        hibernate_settings_path = "/etc/polkit-1/localauthority/50-local.d/lider.ahenk.enable-hibernate.pkla"
        if not self.is_exist(hibernate_settings_path):
            self.logger.info("lider-ahenk.enable-hibernate.pkla does not exist.")
            self.create_file(hibernate_settings_path)
            self.write_file(hibernate_settings_path, temp_hibernate.format(a))
            self.logger.info("Create file and write hibernate data to {0} file ".format(hibernate_settings_path))
            self.logger.info("Enabled hibernate successfully")

        else:
            self.logger.info("{} file already exists".format(hibernate_settings_path))
            line = self.read_file(hibernate_settings_path)
            if "ResultActive=no" in line:
                file_data = line.replace("ResultActive=no", "ResultActive=yes")
                self.write_file(hibernate_settings_path, file_data)
                self.logger.info("Enabled hibernate successfully")
            else:
                file_data = line.replace("ResultActive=yes", "ResultActive=no")
                self.write_file(hibernate_settings_path, file_data)
                self.logger.info("Disabled hibernate successfully")


def handle_task(task, context):
    print('Sample Plugin Task')
    app = DesktopSettings(task, context)
    app.handle_task()
