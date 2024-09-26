# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.calendar.models.calendar import get_real_ids

from odoo.tools import pycompat


class Attachment(models.Model):
    _inherit = "ir.attachment"

    job_title = fields.Char(string='Job Title', compute='_get_title')
    job_position = fields.Char(string='Job position', )
    applicant_id = fields.Many2one('hr.applicant',string="Applicant", compute='_get_title')

    @api.multi
    def _get_title(self):
        for record in self:
            title_id = self.env['ir.attachment'].search(
                ['&', ('res_model', '=', 'hr.applicant'), ('id', '=', record.id)])
            for records in title_id:
                data = self.env['hr.applicant'].sudo().search([('id', '=', records.res_id)])
                record.job_title = data.name
                record.job_position = data.job_position.title
                record.applicant_id = data.id