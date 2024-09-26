
from datetime import date
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class DocumentMaster(models.Model):
    _name = 'emp_document_master'
    _description = 'Employee Document Master'

    name = fields.Char(string="Document Type")
    description = fields.Text(string="Description")