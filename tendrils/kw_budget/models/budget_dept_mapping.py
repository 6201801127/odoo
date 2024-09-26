from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime


class BudgetDepartmentMapping(models.Model):
    _name = 'kw_budget_dept_mapping'
    _description = "Mapping department budget"
    _rec_name = 'name'


    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    budget_type = fields.Selection([('blank', ' '),('Treasury/Capital', 'Treasury/Capital'), ('SBU-Project', 'SBU-Project')
                              ], required=True, string='Budget Type', track_visibility='always', default='blank')
    fiscal_year = fields.Many2one('account.fiscalyear', 'Fiscal Year', default=_default_financial_yr, required=True)
    department_id = fields.Many2one('hr.department', 'Department')
    division_id = fields.Many2one('hr.department', 'Division')
    section_id = fields.Many2one('hr.department', 'Section')
    name = fields.Char('Name', compute='get_namee', store=False)
    level_1_approver = fields.Many2many('hr.employee','kw_budget_approver_l1_rel','employee_id','budget_dept_id',string="1st Level Compiler")
    level_2_approver = fields.Many2many('hr.employee','kw_budget_approver_l2_rel','employee_id','budget_dept_id',string="2nd Level Finalization")
    level_1_approver_capital = fields.Many2many('hr.employee', 'kw_budget_approver_l1_capital_rel', 'employee_id', 'budget_dept_id',
                                        string="1st Level Compiler")
    level_2_approver_capital = fields.Many2many('hr.employee', 'kw_budget_approver_l2_capital_rel', 'employee_id', 'budget_dept_id',
                                        string="2nd Level Finalization")
    active = fields.Boolean(string='Active', default=True)
    capital_boolean = fields.Boolean('Capital')
    revenue_boolean = fields.Boolean('Revenue')
    state = fields.Selection([('draft', 'Applied'), ('approve', 'Approved')
                              ], required=True, string='Status', track_visibility='always', default='draft')

    sbu_id = fields.Many2one("kw_sbu_master", string="SBU")
    sbu_boolean = fields.Boolean('SBU')
    level_1_approver_sbu = fields.Many2many('hr.employee', 'kw_sbu_approver_l1_budget_rel', 'employee_id', 'sbu_emp_id',
                                        string="1st Level Compiler")
    level_2_approver_sbu = fields.Many2many('hr.employee', 'kw_sbu_approver_l2_budget_rel', 'employee_id', 'sbu_emp_id',
                                        string="2nd Level Finalization")

    @api.onchange('department_id')
    def get_value_dept(self):
        self.division_id = False
        self.section_id = False

    @api.onchange('division_id')
    def get_value(self):
        self.section_id = False

    @api.onchange('budget_type')
    def onchange_sbu_bool(self):
        if self.budget_type == 'SBU=Project':
            self.sbu_boolean = True
            self.capital_boolean = False
            self.revenue_boolean = False
        # elif self.budget_type == 'Treasury/Capital':

        else:
            self.sbu_boolean = False

    @api.onchange('capital_boolean', 'revenue_boolean', 'sbu_boolean', 'budget_type')
    def onchange_data(self):
        if self.budget_type == 'Treasury/Capital':
            self.sbu_boolean = False
            self.sbu_id = False
            self.level_1_approver_sbu = [(5, 0, 0)]
            self.level_2_approver_sbu = [(5, 0, 0)]
            if not self.capital_boolean:
                self.level_1_approver_capital = [(5, 0, 0)]
                self.level_2_approver_capital = [(5, 0, 0)]
            if not self.revenue_boolean:
                self.level_1_approver = [(5, 0, 0)]
                self.level_2_approver = [(5, 0, 0)]
        if self.budget_type == 'SBU-Project':
            self.department_id = False
            self.division_id = False
            self.section_id = False
            self.level_1_approver_capital = [(5, 0, 0)]
            self.level_2_approver_capital = [(5, 0, 0)]
            self.level_1_approver = [(5, 0, 0)]
            self.level_2_approver = [(5, 0, 0)]
            self.capital_boolean = False
            self.revenue_boolean = False
            self.sbu_boolean = True



    def get_namee(self):
        for rec in self:
            if rec.budget_type == 'Treasury/Capital':
                department_name = rec.department_id.name or ''
                division_name = rec.division_id.name or ''
                section_name = rec.section_id.name or ''
                rec.name = '-'.join(filter(None, [department_name, division_name, section_name]))
            if rec.budget_type == 'SBU-Project':
                rec.name = rec.sbu_id.display_name



    @api.constrains('fiscal_year')
    def _check_duplicate_department_id(self):
        current_fiscal = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        if self.budget_type == 'Treasury/Capital':
            for record in self:
                duplicate_records = self.search([
                    ('department_id', '=', record.department_id.id),
                    ('division_id', '=', record.division_id.id),
                    ('section_id', '=', record.section_id.id),
                    ('id', '!=', record.id),
                    ('fiscal_year', '=', current_fiscal.id)
                ])
                if duplicate_records:
                    raise ValidationError("Duplicate department name is not allowed!")
        if self.budget_type == 'SBU-Project':
            for rec in self:
                duplicate_records = self.search([
                    ('sbu_id', '=', rec.sbu_id.id),
                    ('id', '!=', rec.id),
                    ('fiscal_year', '=', current_fiscal.id)
                ])
                if duplicate_records:
                    raise ValidationError("Duplicate  SBU name is not allowed!")

    def start_budget(self):
        if self.state == 'draft':
            if self.user_has_groups('kw_budget.group_cfo_kw_budget'):
                self.state = 'approve'
            else:
                raise ValidationError("You are not allowed to start the Budget !!.")

    @api.model
    def _update_group_users(self):
        l2_grp_list = set()
        l1_capital = set()
        l2_capital = set()
        dataa = set()
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        approved_mappings = self.env['kw_budget_dept_mapping'].search([('state', '=', 'approve'), ('fiscal_year', '=', current_fiscal.id)])

        for rec in approved_mappings:
            if rec.revenue_boolean:
                dataa.update(emp.user_id.id for emp in rec.level_1_approver)
                dataa.update(emp.user_id.id for emp in rec.level_2_approver)
                l2_grp_list.update(emp.user_id.id for emp in rec.level_2_approver)

            if rec.capital_boolean:
                l1_capital.update(emp.user_id.id for emp in rec.level_1_approver_capital)
                l1_capital.update(emp.user_id.id for emp in rec.level_2_approver_capital)
                l2_capital.update(emp.user_id.id for emp in rec.level_2_approver_capital)

            if rec.budget_type == 'SBU-Project':
                dataa.update(emp.user_id.id for emp in rec.level_1_approver_sbu)
                dataa.update(emp.user_id.id for emp in rec.level_2_approver_sbu)

        # Convert sets back to lists for the group updates
        final_data = list(dataa)
        capital = list(l1_capital | l2_capital)  # Union of l1_capital and l2_capital

        # Update groups in batch
        self.env.ref('kw_budget.group_department_head_kw_budget').sudo().write({'users': [(6, 0, final_data)]})
        self.env.ref('kw_budget.group_l2_kw_budget').sudo().write({'users': [(6, 0, list(l2_grp_list))]})
        self.env.ref('kw_budget.group_capital_budget_user_kw_budget').sudo().write({'users': [(6, 0, capital)]})
        self.env.ref('kw_budget.group_revenue_budget_user_kw_budget').sudo().write({'users': [(6, 0, final_data)]})

    @api.model
    def _update_sbu_project_group_users(self):
        user_ids = set()  # Use a set to avoid duplicates
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        sbu_projects = self.env['kw_sbu_project_mapping'].search([('fiscal_year_id', '=', current_fiscal.id)])

        for rec in sbu_projects:
            user_ids.update(emp.user_id.id for emp in rec.level_1_approver)
            user_ids.update(emp.user_id.id for emp in rec.level_2_approver)

        # Convert set back to list for the group update
        user_ids_list = list(user_ids)
        group_department_head_kw_budget = self.env.ref('kw_budget.group_department_head_kw_budget').sudo()
        group_department_head_kw_budget.write({'users': [(6, 0, user_ids_list)]})

    @api.multi
    def write(self, vals):
        res = super(BudgetDepartmentMapping, self).write(vals)

        if self.state == 'approve':
            self._update_group_users()

            sbu_obj_find = self.env['kw_sbu_project_mapping'].sudo()
            sbu_obj_find_result = sbu_obj_find.search([
                ('sbu_id', '=', self.sbu_id.id),
                ('fiscal_year_id', '=', self.fiscal_year.id)
            ])

            # Only proceed if we found relevant SBU mappings
            if sbu_obj_find_result:
                # Prepare a dictionary to hold the updates
                data_dict = {}
                if 'level_1_approver_sbu' in vals:
                    data_dict['level_1_approver'] = vals['level_1_approver_sbu']

                if 'level_2_approver_sbu' in vals:
                    data_dict['level_2_approver'] = vals['level_2_approver_sbu']

                # Write the collected updates
                if data_dict:
                    sbu_obj_find_result.write(data_dict)
                    sbu_obj_find_result._update_project_group_users()

        return res

    def action_done_show_wizard(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Budget Start'),
                'res_model': 'budget.department.mapping',
                'target': 'new',
                'view_id': self.env.ref('kw_budget.kw_budget_department_mapping_start').id,
                'view_mode': 'form',
                'context': {'active_ids': self.ids},
                }

