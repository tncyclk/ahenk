#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.content_type import ContentType
import json

class Sample(AbstractPlugin):
    def __init__(self, task, context):
        super(Sample, self).__init__()
        self.task = task
        self.message_code = self.get_message_code()
        self.context = context
        self.logger = self.get_logger()
        self.eta_notify_command_fullscreen = "DISPLAY=:0 eta-notify -m  \"{message_content}\" -d {duration}"
        self.eta_notify_command_small = "DISPLAY=:0 eta-notify -m  \"{message_content}\" -d {duration} --{size}"
        self.message_content = None

    def handle_task(self):
        try:
            self.message_content = self.task['notify_content']
            message_duration = self.task['duration']
            message_size = self.task['size']
            if self.task['size'] == 'small':
                result_code, p_out, p_err = self.execute(self.eta_notify_command_small.format(message_content=self.message_content, duration=message_duration, size=message_size))
                self.create_response(result_code, p_err)

            else:
                result_code, p_out, p_err = self.execute(self.eta_notify_command_fullscreen.format(message_content=self.message_content, duration=message_duration))
                self.create_response(result_code, p_err)

        except Exception as e:
            self.logger.error("*********"+str(e))
            self.context.create_response(code=self.message_code.TASK_PROCESSED.TASK_ERROR.value,
                                         message='Bilgilendirme Mesajı görevi çalıştırılırken hata oluştu.!',
                                         content_type=ContentType.APPLICATION_JSON.value)

    def create_response(self, result_code, p_err):
        self.save_notify(result_code)

        if result_code == 0:
            self.logger.info("Successfully executed ETAP Notify Message ")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Bilgilendirme Mesajı görevi başarıyla çalıştırıldı',
                                         content_type=ContentType.APPLICATION_JSON.value)
        else:
            self.logger.error("Failed to executed ETAP Notify Message. ERROR: "+str(p_err))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Bilgilendirme Mesajı görevi çalıştırılırken hata oluştu',
                                         content_type=ContentType.APPLICATION_JSON.value)


    def save_notify(self, result_code):
        if result_code == 0:
            status = True
        else:
            status = False

        cols = ['send_time', 'content', 'duration', 'status']
        values = [self.task["send_time"], self.task["notify_content"], self.task["duration"],status]
        self.db_service.update('notify', cols, values)
        self.logger.debug("Saved notify to ahenk.db")

def handle_task(task, context):
    print('Sample Plugin Task')
    sample = Sample(task, context)
    sample.handle_task()
