# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, _


class Orientation(models.Model):
    _name = 'employee.orientation'
    _description = "Employee Orientation"
    _inherit = 'mail.thread'

    name = fields.Char(string='Employee Orientation /कर्मचारी उन्मुखीकरण', readonly=True, default=lambda self: _('New'))
    employee_name = fields.Many2one('hr.employee', string='Employee /कर्मचारी', size=32, required=True)
    department = fields.Many2one('hr.department', string='Department /विभाग', related='employee_name.department_id',
                                 required=True)
    date = fields.Datetime(string="Date /तारीख")
    # date = fields.Datetime.to_string(dateText)
    responsible_user = fields.Many2one('res.users', string='Responsible User /जिम्मेदार उपयोगकर्ता')
    employee_company = fields.Many2one('res.company', string='Company /कंपनी', required=True,
                                       default=lambda self: self.env.user.company_id)
    parent_id = fields.Many2one('hr.employee', string='Manager /प्रबंधक', related='employee_name.parent_id')
    job_id = fields.Many2one('hr.job', string='Job Title /नौकरी का नाम', related='employee_name.job_id',
                             domain="[('department_id', '=', department)]")
    orientation_id = fields.Many2one('orientation.checklist', string='Orientation Checklist /ओरिएंटेशन चेकलिस्ट',
                                     domain="[('checklist_department','=', department)]", required=True)
    note_id = fields.Text('Description /विवरण')
    orientation_request = fields.One2many('orientation.request', 'request_orientation', string='Orientation Request /अभिविन्यास अनुरोध')
    state = fields.Selection([
        ('draft', 'Draft /प्रारूप'),
        ('confirm', 'Confirmed /की पुष्टि'),
        ('cancel', 'Canceled /रद्द'),
        ('complete', 'Completed /पुरा होना'),
    ], string='Status /दर्जा', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def confirm_orientation(self):
        self.write({'state': 'confirm'})
        for values in self.orientation_id.checklist_line_id:
            self.env['orientation.request'].create({
                'request_name': values.line_name,
                'request_orientation': self.id,
                'partner_id': values.responsible_user.id,
                'request_date': self.date,
                'employee_id': self.employee_name.id,
            })

    def cancel_orientation(self):
        for request in self.orientation_request:
            request.state = 'cancel'
        self.write({'state': 'cancel'})

    def complete_orientation(self):
        force_complete = False
        for request in self.orientation_request:
            if request.state == 'new':
                force_complete = True
        if force_complete:
            return {
                'name': 'Complete Orientation',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'orientation.force.complete',
                'type': 'ir.actions.act_window',
                'context': {'default_orientation_id': self.id},
                'target': 'new',
            }
        self.write({'state': 'complete'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.orientation')
        result = super(Orientation, self).create(vals)
        return result
