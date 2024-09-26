from odoo import models, fields, api


class kw_eligibility_amnt_exec(models.Model):
    _name = 'kw_advance_eligibility_amnt_exec'
    _description = "Advance Eligibility Amount Exception"
    # _rec_name = 'location_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # location_id = fields.Many2one('kw_res_branch', string="Branch / SBU", required=True, track_visibility='onchange')
    # location_name = fields.Char('Location', related='location_id.location.name', store=True)
    # group_id=fields.Many2one('kw_advance_claim_groups', string="Group",required=True,track_visibility='onchange')
    dept_id = fields.Many2one('hr.department', string="Department", required=True, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee(s)", required=True, track_visibility='onchange')
    amnt = fields.Integer(string="Amount", required=True, track_visibility='onchange')
    active = fields.Boolean(string="Active", default=True)
    # division = fields.Many2one('hr.department', string="Division")
    # section = fields.Many2one('hr.department', string="Section")
    practise = fields.Many2one('hr.department', string="Practise")

    @api.onchange('division')
    def _onchange_division(self):
        lst = []
        self.employee_id = False
        self.section = False
        for record in self:
            emp_record = self.env['hr.employee'].sudo().search([('division', '=', record.division.id)])
            print(emp_record)
            if emp_record:
                for rec in emp_record:
                    lst.append(rec.id)

        return {'domain': {'employee_id': [('id', 'in', lst)]}}

    @api.onchange('dept_id')
    def _onchange_dept_id(self):
        lst = []
        self.division = False
        for record in self:
            emp_dept_record = self.env['hr.employee'].sudo().search([('department_id', '=', record.dept_id.id)])
            if emp_dept_record:
                for rec in emp_dept_record:
                    lst.append(rec.id)

        return {'domain': {'employee_id': [('id', 'in', lst)]}}

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
