#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json

class ResourceUsage(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            # phase info for eta
            processor = self.Hardware.Cpu.brand()
            # processor for Vestel
            if processor == "Intel i3 2330M - 2.20GHz - 3MB":
                phase = "Faz 1"
            elif processor == "Intel i3 3120M - 2.50GHz - 3MB":
                phase = "Faz 2"
            elif processor == "AMD A10-5750M - 2.5GHz - 4MB":
                phase = "Faz 2"
            elif processor == "Intel i3 4000M - 2.40GHz - 3MB":
                phase = "Faz 2"
            # processor for Arcelik
            elif processor == "Intel(R) Core(TM) i3-8100T CPU @ 3.10GHz":
                phase = "Faz 3"
            else:
                phase = 0


            device = ""
            self.logger.debug("Gathering resource usage for disk, memory and CPU.")
            for part in self.Hardware.Disk.partitions():
                if len(device) != 0:
                    device += ", "
                device = device + part.device
            data = {'System': self.Os.name(), 'Release': self.Os.kernel_release(),
                    'Version': self.Os.distribution_version(), 'Machine': self.Os.architecture(),
                    'CPU Physical Core Count': self.Hardware.Cpu.physical_core_count(),
                    'Total Memory': self.Hardware.Memory.total(),
                    'Usage': self.Hardware.Memory.used(),
                    'Total Disc': self.Hardware.Disk.total(),
                    'Usage Disc': self.Hardware.Disk.used(),
                    'Processor': self.Hardware.Cpu.brand(),
                    'Device': device,
                    'CPU Logical Core Count': self.Hardware.Cpu.logical_core_count(),
                    'CPU Actual Hz': self.Hardware.Cpu.hz_actual(),
                    'CPU Advertised Hz': self.Hardware.Cpu.hz_advertised(),
                    'Phase': phase
                    }
            self.logger.debug("Resource usage info gathered.")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Anlık kaynak kullanım bilgisi başarıyla toplandı.',
                                         data=json.dumps(data),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Anlık kaynak kullanım bilgisi toplanırken hata oluştu: {0}'.format(
                                             str(e)))


def handle_task(task, context):
    plugin = ResourceUsage(task, context)
    plugin.handle_task()
