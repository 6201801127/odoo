# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import pdb

class NoticePeriodMaster(models.Model):
    _name = "kw_notice_period_master"
    _description = "Notice Period Master"
    _rec_name = 'group_id'
    _order = 'id'

    group_id = fields.Many2one('kw_emp_group_master', string="Group", required=True)
    grade_ids = fields.Many2many('kwemp_grade_master', 'np_grade_rel', 'band_id','grade_id',string="Grade",required=True)
    band_ids = fields.Many2many('kwemp_band_master', 'np_band_rel', 'band_id','grade_id',string="Band")
    notice_period = fields.Integer(string="Notice Period (Days)",required=True)
    sequence = fields.Integer(
        "Sequence", default=0,
        help="Gives the sequence order of qualification.")

    """ Restrict dublicate entries """
    @api.onchange('grade_ids','band_ids')
    def onchange_grade_band(self):
        domain = []
        for rec in self:
            if rec.grade_ids and rec.band_ids:
                domain += [('grade_ids','in',rec.grade_ids.ids),('band_ids','in',rec.band_ids.ids)]
            # if rec.grade_ids and not rec.band_ids:
                # domain += [('grade_ids','in',rec.grade_ids),('band_ids','=',False)]
        if domain:
            record_ids = self.env['kw_notice_period_master'].search(domain)
            if record_ids:
                raise ValidationError('Record With the Selected Grade/Band already exist.')
        
    