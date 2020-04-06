#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Tucnay ÇOLAK <tuncay.colak@tubitak.gov.tr>

## user-based application restriction for etap 

from base.plugin.abstract_plugin import AbstractPlugin

class AppRestriction(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.applications = []
        self.exist_app_list = []

    def handle_task(self):
        try:
            self.applications = self.task['applicationList']
            self.exist_app_list = self.task['isExistAppList']

            if len(self.exist_app_list) > 0:
                self.remove_restriction_to_app()

            if len(self.applications) > 0:
                self.add_restiction_to_app()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Uygulama başarıyla kısıtlandı',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Uygulama kısıtlanırken hata oluştu: {0}'.format(str(e)))

    def remove_restriction_to_app(self):

        for exist_app_name in self.exist_app_list:
            self.logger.info("Revert permission "+str(exist_app_name))
            exe_app = self.get_executable_path(exist_app_name)
            self.logger.debug("Find executable path {0} 's ".format(exist_app_name) + str(exe_app))
            result_code, p_out, p_err = self.execute("ls -l {0}".format(exe_app))
            p_out = p_out.strip("\n").split(" ")[-1]

            if exe_app is not None:
                if p_out == exe_app:
                    self.set_default_mode_to_app(exe_app)
                else:
                    if "../" in p_out:
                        p_out = p_out.replace("../", "/usr/")
                        self.set_default_mode_to_app(p_out)

                    elif not "../" and "/" in p_out:
                        if "/sbin/" in p_out:
                            p_out = "/usr/sbin/" + str(p_out)
                            self.set_default_mode_to_app(p_out)
                        if "/bin/" in p_out:
                            p_out = "/usr/bin/" + str(p_out)
                            self.set_default_mode_to_app(p_out)
                    else:
                        self.set_default_mode_to_app(p_out)
            else:
                self.logger.debug("Not found executable path {0}".format(exist_app_name))

        self.db_service.delete('app_restriction', None)

    def add_restiction_to_app(self):
        for app in self.applications:
            app_name = app['app_name']
            username = app['username']
            restriction = app['restriction']

            exe_app_path = self.get_executable_path(app_name)
            self.logger.debug("Find executable path {0} 's ".format(app_name) + str(exe_app_path))

            if exe_app_path is not None:
                result_code, p_out, p_err = self.execute("ls -l {0}".format(exe_app_path))
                p_out = p_out.strip("\n").split(" ")[-1]

                if p_out == exe_app_path:
                    self.change_mode_to_app(app, exe_app_path)
                else:
                    if "../" in p_out:
                        p_out = p_out.replace("../", "/usr/")
                        self.change_mode_to_app(app, p_out)

                    elif not "../" and "/" in p_out:
                        if "/sbin/" in p_out:
                            p_out = "/usr/sbin/" + str(p_out)
                            self.change_mode_to_app(app, p_out)
                        if "/bin/" in p_out:
                            p_out = "/usr/bin/" + str(p_out)
                            self.change_mode_to_app(app, p_out)
                    else:
                        self.change_mode_to_app(app, p_out)
            else:
                self.logger.debug("Not found executable path {0}".format(app_name))

    # permissions of applications changed for restricted
    def change_mode_to_app(self, app, exe_app_path):

        self.change_owner(exe_app_path, "root", "floppy")
        self.logger.info("Changed owner {0}".format(exe_app_path))
        self.execute("chmod 754 {0}".format(exe_app_path))
        self.logger.info("Changed chmod {0}".format(exe_app_path))
        self.save_application(app)

    # revert permissions of applications changed
    def set_default_mode_to_app(self, exe_app):
        self.change_owner(exe_app, "root", "root")
        self.logger.info("Revert owner {0}".format(exe_app))
        self.execute("chmod 755 {0}".format(exe_app))
        self.logger.info("Revert chmod {0}".format(exe_app))

    def save_application(self, app):
        cols = ['application_name', 'username', 'restriction']
        values = [app["app_name"], app["username"], app["restriction"]]

        self.logger.debug("Delete from app_restriction table")
        self.db_service.update('app_restriction', cols, values)
        self.logger.debug("Saved applications to ahenk.db")

def handle_task(task, context):
    plugin = AppRestriction(task, context)
    plugin.handle_task()
