# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PaticularsMaster(models.Model):
    _name = 'kw_eq_paticulars_master'
    _description = 'Paticulars Master'

    
    paticulars = fields.Char(string='Particulars')
    code = fields.Char(string="Code")



class PaticularsConfig(models.Model):
    _name = 'kw_eq_paticulars_config'
    _description = 'Paticulars Configuration'

    paticular_id = fields.Many2one('kw_eq_estimation')
    revision_paticular_id = fields.Many2one('kw_eq_revision')
    paticular_replica_id = fields.Many2one('kw_eq_replica')
    paticulars_name = fields.Char(string='Particulars')
    amount = fields.Float(string="Amount")
    code = fields.Char(string="Code")
