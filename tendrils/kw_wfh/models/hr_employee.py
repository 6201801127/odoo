from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from datetime import date, datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    def check_wfh(self):
        for rec in self:
            today_date = date.today()
            domain = [('employee_id', '=', rec.id), ('state', 'in', ['grant']),
                      ('request_from_date', '<=', today_date), ('request_to_date', '>=', today_date)]
            rec.is_wfh = self.env['kw_wfh'].sudo().search(domain).exists()

    is_wfh = fields.Boolean('WFH', default=False, store=False, readonly=False, compute='check_wfh')

    @api.depends('is_wfh')
    def _compute_get_wfh_info(self):
        today = datetime.today().date()
        for record in self:
            if record.is_wfh:
                wfh = self.env['kw_wfh'].search([('emp_id', '=', record.id), ('state', '=', 'grant'),
                                                 ('request_from_date', '<=', today), ('request_to_date', '>=', today)], limit=1)

                if wfh:
                    record.citrix_access = wfh.citrix_access
                    record.computer_info = wfh.computer_info
                    record.inter_connectivity = wfh.inter_connectivity
                else:
                    record.citrix_access = ''
                    record.computer_info = False
                    record.inter_connectivity = ''

    citrix_access = fields.Selection(string="Citrix Accessibility Required?", selection=[('yes', 'Yes'), ('no', 'No')], default='no', compute='_compute_get_wfh_info')
    computer_info = fields.Many2one('kw_system_info', string="Computer Information",compute='_compute_get_wfh_info')
    inter_connectivity = fields.Selection(string="Internet Connection",
                                          selection=[('yes', 'Mobile Data'), ('no', 'Hotspot'), ('broadband', 'Broadband')], default='yes',
                                          compute='_compute_get_wfh_info')
