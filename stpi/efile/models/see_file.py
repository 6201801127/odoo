from odoo import fields, models, api

class FolderMaster(models.Model):
    _name = 'see.file'
    _description='See File'

    my_url = fields.Text()
    my_url_text = fields.Text()

