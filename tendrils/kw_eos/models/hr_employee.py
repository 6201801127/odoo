# -*- coding: utf-8 -*-
from odoo import models, fields, api


class hr_employee_in(models.Model):
    _inherit = 'hr.employee'

    # last_working_date = fields.Date('Last Working Date')
    in_noticeperiod = fields.Boolean('In Notice Period', default=False)
    # resignation_aplied = fields.Boolean('Resignation Applied', default=False)
    resignation_reason = fields.Many2one('kw_resignation_master', readonly=True, string="Resignation Type",
                                         track_visibility='onchange')
    attrition_type = fields.Selection([('vountary', 'Voluntary'), ('involuntary', 'Involuntary')], 'Attrition Type',
                              track_visibility='onchange',)   
    tenure_months = fields.Integer(compute='_compute_tenure_months')
    
    involuntary_reason = fields.Selection([('contract_closure', 'Contract Closure'), ('demise', 'Demise'),('retirement','Retirement'),('performance_issue','Performance Issue'),('termination','Termination')], 'Attrition Type',
                              track_visibility='onchange',)  

    @api.depends('date_of_joining', 'last_working_day')
    def _compute_tenure_months(self):
        for employee in self:
            if employee.date_of_joining and employee.last_working_day:
                joining_date = fields.Date.from_string(employee.date_of_joining)
                last_working_date = fields.Date.from_string(employee.last_working_day)
                tenure_months = (last_working_date.year - joining_date.year) * 12 + (last_working_date.month - joining_date.month)
                employee.tenure_months = tenure_months
            else:
                employee.tenure_months = 0
                
    def button_active(self):
        for record in self:
            form_view_id = self.env.ref('kw_eos.kw_emp_archieve_view_form')

            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': form_view_id.id,
                'res_model': 'kw_emp_archieve',
                'target': 'new',
            }
