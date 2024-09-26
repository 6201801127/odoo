from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_interest_exec(models.Model):
    _name = 'kw_advance_interest_exec'
    _description = "Advance Interest Exception"
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    location_id = fields.Many2one('kw_res_branch', string="Branch / SBU", required=True, track_visibility='onchange')
    group_id = fields.Many2one('kw_advance_claim_groups', string="Group", track_visibility='onchange')
    dept_id = fields.Many2one('hr.department', string="Department", required=True, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee(s)", required=True, track_visibility='onchange')
    interest = fields.Integer(string="Interest(%)", required=True, track_visibility='onchange')
    active = fields.Boolean(string="Active", default=True)
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")

    @api.constrains('interest')
    def validate_interest(self):
        for record in self:
            if record.interest < 0:
                raise ValidationError("Interest cannot be 0 or less than 0.")
            elif record.interest > 100:
                raise ValidationError("Interest cannot be greater than 100.")
            else:
                return True

    @api.onchange('division')
    def _onchange_division(self):
        # print("method called")
        divsion_lst = []
        self.employee_id = False
        self.section = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search([('division', '=', record.division.id)])
            # print(emp_div_record)
            if emp_div_record:
                for rec in emp_div_record:
                    divsion_lst.append(rec.id)

        return {'domain': {'employee_id': [('id', 'in', divsion_lst)]}}

    @api.onchange('dept_id')
    def _onchange_dept_id(self):
        dept_lst = []
        self.division = False
        for record in self:
            emp_dept_record = self.env['hr.employee'].sudo().search([('department_id', '=', record.dept_id.id)])
            if emp_dept_record:
                for rec in emp_dept_record:
                    dept_lst.append(rec.id)

        return {'domain': {'employee_id': [('id', 'in', dept_lst)]}}

    @api.onchange('dept_id')
    def onchange_department(self):
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.dept_id.id), ('dept_type.code', '=', 'division')]
            return {'domain': domain}

    @api.onchange('division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.dept_id:
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.section:
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                return {'domain': domain}
