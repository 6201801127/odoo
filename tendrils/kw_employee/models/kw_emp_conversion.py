# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError



class kw_emp_conversion(models.Model):
    _name = 'kw_emp_conversion'
    _description= 'Model to Change Employment Type'

    search_by = fields.Selection(string="Search By",
                                 selection=[('1', 'RET-Overhead'), ('2', 'RET-Project'), ('3', 'Offshore'),
                                            ('4', 'Contractual Outsourced')], default="1")
    employee_id = fields.Many2one('hr.employee',string="Employee")

    @api.onchange('search_by')
    def get_emp(self):
        ret_overhead_lst = []
        ret_project_lst = []
        offshore_lst = []
        contractual_lst = []
        employee = self.env['hr.employee'].sudo().search([])
        for record in employee:
            if record.employement_type.name == 'RET-Overhead':
                ret_overhead_lst.append(record.id)
            if record.employement_type.name == 'RET-Project':
                ret_project_lst.append(record.id)
            if record.employement_type.name == 'Offshore':
                offshore_lst.append(record.id)
            if record.employement_type.name == 'Contractual Outsourced':
                contractual_lst.append(record.id)

        if self.search_by == '1':
            self.employee_id = False
            return {'domain': {'employee_id': [('id', 'in', ret_overhead_lst)]}}
        if self.search_by == '2':
            self.employee_id = False
            return {'domain': {'employee_id': [('id', 'in', ret_project_lst)]}}
        if self.search_by == '3':
            self.employee_id = False
            return {'domain': {'employee_id': [('id', 'in', offshore_lst)]}}
        if self.search_by == '4':
            self.employee_id = False
            return {'domain': {'employee_id': [('id', 'in', contractual_lst)]}}
 
    @api.multi
    def view_form(self):
        check_active_id = self.env['kw_emp_conversion'].browse(self.id)
        form_view_id = self.env.ref("kw_employee.kw_emp_conversion_view_form")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_emp_conversion',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': check_active_id.id,
            'view_id': form_view_id.id,
            'target': 'self',
            'flags': {'mode': 'edit', "toolbar": False}
        }
    