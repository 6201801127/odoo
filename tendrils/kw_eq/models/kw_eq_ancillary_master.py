# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AncillaryMaster(models.Model):
    _name = 'kw_eq_ancillary_master'
    _description = 'Ancillary configuration'

    name = fields.Char('Category Name')
    category_in = fields.Boolean('Category In')

    


class AncillaryItemMaster(models.Model):
    _name = 'kw_eq_ancillary_item_master'
    _description = 'Ancillary Itemconfiguration'
    _rec_name = 'item'
    _order = 'ancillary_id'

    ancillary_id = fields.Many2one('kw_eq_ancillary_master')
    section = fields.Selection([('1', 'Section 1'),('2', 'Section 2'),('3', 'Section 3'),('4','Section 4'),('5','Section 5'),('6','Section 6'),('7','Section 7'),('8','Section 8'),('9','Section 9')], string='Section')# Section 2 is used for Total [Operation & Support] ,3 is used for Out Of Pocket Expenditure,5 is used for reimbursement,6 is used for strategic partner sharing ,1 is used for Third Party Audit andthe left are assigned to 4
    item = fields.Char()
    unit = fields.Char()
    sort_no = fields.Integer()