from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class kw_adv_ret_config(models.Model):
    _name = 'kw_advance_ret_config'
    _description = "RET Configuration"
    # _rec_name = 'location_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # location_id = fields.Many2one('kw_res_branch', string="Branch / SBU", required=True, track_visibility='onchange')
    # location_name = fields.Char('Location', related='location_id.location.name', store=True)
    group_id = fields.Many2one('kw_advance_claim_groups', string="Group", track_visibility='onchange')
    employee_ids = fields.Many2many('hr.employee', 'kw_advance_ret_config_hr_employee_rel', 'config_id',
                                    'employee_id', string="Employee(s)", required=True, track_visibility='onchange')
    """# salary advance/petty cash/both all are in horizontal radio button"""
    # sal_advance = fields.Selection(string="Salary Advance", selection=[('yes', 'Yes'), ('no', 'No')],required=True,track_visibility='onchange') # salary advance/petty cash/both all are inhorizontal radio button
    # petty_cash = fields.Selection(string="Petty Cash", selection=[('yes', 'Yes'), ('no', 'No')],required=True,track_visibility='onchange') # salary advance/petty cash/both all are inhorizontal radio button
    dept_id = fields.Many2one('hr.department', string="Department")
    # division = fields.Many2one('hr.department', string="Division")
    # section = fields.Many2one('hr.department', string="Section")
    # practise = fields.Many2one('hr.department', string="Practise")
    active = fields.Boolean(string="Active", default=True)
    remark = fields.Text(string="Remark", track_visibility='onchange')
    documents = fields.Binary(string='Document', attachment=True, track_visibility='onchange')
    file_name = fields.Char("File Name", track_visibility='onchange')
    eligibility_amt = fields.Float(string="Advance Amount", required=True, track_visibility='onchange')
    interest = fields.Integer(string='Interest(% per Annum)', required=True, track_visibility='onchange')

    @api.onchange('practise')
    def _onchange_practise(self):
        practise_lst = []
        self.employee_ids = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('practise', '=', record.practise.id), ('employement_type', 'not in', 'FTE'),
                 ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                # for rec in emp_div_record:
                #     practise_lst.append(rec.id)
                return {'domain': {'employee_ids': [('id', 'in', emp_div_record.ids)]}}

    @api.onchange('section')
    def _onchange_section(self):
        section_lst = []
        self.employee_ids = False
        self.practise = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('section', '=', record.section.id), ('employement_type', 'not in', 'FTE'),
                 ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                # for rec in emp_div_record:
                #     section_lst.append(rec.id)
                return {'domain': {'employee_ids': [('id', 'in', emp_div_record.ids)]}}

    @api.onchange('division')
    def _onchange_division(self):
        division_lst = []
        self.employee_ids = False
        self.section = False
        for record in self:
            emp_div_record = self.env['hr.employee'].sudo().search(
                [('division', '=', record.division.id), ('employement_type', 'not in', 'FTE'),
                 ('job_branch_id', '=', self.location_id.id)])
            if emp_div_record:
                # for rec in emp_div_record:
                #     division_lst.append(rec.id)
                return {'domain': {'employee_ids': [('id', 'in', emp_div_record.ids)]}}

    @api.onchange('dept_id')
    def _onchange_dept_id(self):
        dept_lst = []
        self.division = False
        for record in self:
            emp_dept_record = self.env['hr.employee'].sudo().search(
                [('department_id', '=', record.dept_id.id), ('employement_type', 'not in', 'FTE'),
                 ('job_branch_id', '=', self.location_id.id)])
            if emp_dept_record:
                # for rec in emp_dept_record:
                #     dept_lst.append(rec.id)
                return {'domain': {'employee_ids': [('id', 'in', emp_dept_record.ids)]}}

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

    @api.model
    def create(self, vals):
        res = super(kw_adv_ret_config, self).create(vals)
        user_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_user')
        employees_user_id = res.employee_ids.mapped('user_id')
        for record in employees_user_id:
            if not record.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                user_group.sudo().write({
                    'users': [(4, record.id)]
                })
        # self.env.user.notify_success(message='Employee(s) Exception created successfully')
        return res

    
    def write(self, vals):
        current_employee_ids = self.employee_ids.ids
        employee = self.env['hr.employee']
        user_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_user')

        res = super(kw_adv_ret_config, self).write(vals)
        updated_employee_ids = self.employee_ids.ids
        for current_employee in current_employee_ids:
            if current_employee not in updated_employee_ids:
                current_emp = employee.search([('id', '=', current_employee)]).mapped('user_id')
                if current_emp and current_emp.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                    user_group.sudo().write({
                        'users': [(3, current_emp.id, False)]
                    })
        for update_employee in updated_employee_ids:
            if update_employee not in current_employee_ids:
                update_emp = employee.search([('id', '=', update_employee)]).mapped('user_id')
                if update_emp and not update_emp.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                    user_group.sudo().write({
                        'users': [(4, update_emp.id)]
                    })
        # self.env.user.notify_success(message='Employee(s) Exception updated successfully')
        return res

    @api.onchange('employee_ids')
    def onchange_semployee_ids(self):
        emp_ids = self.employee_ids
        exception_record = self.sudo().search([('employee_ids', 'in', emp_ids.ids)])
        if exception_record:
            raise ValidationError("Multiple exception cannot be created for same employee")
