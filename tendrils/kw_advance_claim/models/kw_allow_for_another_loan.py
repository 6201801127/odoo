from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_allow_for_another_loan(models.Model):
    _name = 'kw_advance_allow_for_another_loan'
    _description = "Allow for another loan"
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    location_id = fields.Many2one('kw_res_branch', string="Branch / SBU", required=True, track_visibility='onchange')
    dept_id = fields.Many2one('hr.department', string="Department", required=True, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, track_visibility='onchange')
    loan_elig_amnt = fields.Integer(string="Loan Eligible Amount", required=True, track_visibility='onchange')
    advance_type_id = fields.Many2one('kw_advance_type', string="Advance Type", required=True,
                                      track_visibility='onchange')
    active = fields.Boolean(string="Active", default=True)
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practise")
    practise = fields.Many2one('hr.department', string="Section")

    @api.onchange('practise')
    def _onchange_practise(self):
        practise_lst = []
        self.employee_ids = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('practise', '=', record.practise.id), ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                for rec in emp_div_record:
                    practise_lst.append(rec.id)

        return {'domain': {'employee_ids': [('id', 'in', practise_lst)]}}

    @api.onchange('section')
    def _onchange_section(self):
        section_lst = []
        self.employee_ids = False
        self.practise = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('section', '=', record.section.id), ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                for rec in emp_div_record:
                    section_lst.append(rec.id)

        return {'domain': {'employee_ids': [('id', 'in', section_lst)]}}

    @api.onchange('division')
    def _onchange_division(self):
        division_lst = []
        self.employee_id = False
        self.section = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('division', '=', record.division.id), ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                for rec in emp_div_record:
                    division_lst.append(rec.id)

        return {'domain': {'employee_id': [('id', 'in', division_lst)]}}

    @api.onchange('dept_id')
    def _onchange_dept_id(self):
        dept_lst = []
        self.division = False
        for record in self:
            emp_dept_record = self.env['hr.employee'].sudo().search(
                [('department_id', '=', record.dept_id.id), ('job_branch_id', '=', self.location_id.id)])
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

    @api.onchange('advance_type_id')
    def onchange_semployee_id(self):
        exception_record = self.sudo().search(
            [('employee_id', '=', self.employee_id.id), ('advance_type_id', '=', self.advance_type_id.id)])
        if exception_record:
            raise ValidationError("Multiple exception cannot be created for same employee")

    @api.model
    def create(self, values):
        if not values.get('advance_type_id'):
            raise ValidationError("Please select Advance Type.")

        exception_record = self.search(
            [('employee_id', '=', values.get('employee_id')), ('advance_type_id', '=', values.get('advance_type_id'))])
        if exception_record:
            raise ValidationError("Multiple exception cannot be created for same employee")

        res = super(kw_allow_for_another_loan, self).create(values)
        self.env.user.notify_success("Record added successfully.")
        return res

    @api.multi
    def write(self, values):
        res = super(kw_allow_for_another_loan, self).write(values)
        self.env.user.notify_success("Record updated successfully.")
        return res
