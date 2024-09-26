from odoo.tools.config import configmanager


class NewConfigmanager(configmanager):
    def __init__(self):
        configmanager.__init__(self)

    def _license_key_list(self):
        license_key_list = ['965A4TY730VG', 'PO9510LK630P', 'QTHNO816774L']
        return license_key_list

obj = NewConfigmanager()
