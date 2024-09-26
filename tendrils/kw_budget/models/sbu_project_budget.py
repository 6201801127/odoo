from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime
import os
import tempfile
import xlsxwriter
import base64
import logging

_logger = logging.getLogger('****************Treasury Budget Report****************')

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
import base64


class AccountingSBUProjectBudget(models.Model):
    _name = 'kw_sbu_project_budget'
    _description = "SBU Project Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "fiscal_year_id"

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    def _get_sbu_user(self):
        domain = [('id', '=', 0)]
        user = self.env.user.employee_ids
        if user:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            domain = []
            budget_sbu_id = self.env['kw_sbu_project_mapping'].search([
                '|', ('level_2_approver.id', '=', user.id),
                ('level_1_approver.id', '=', user.id),
            ('fiscal_year_id', '=', current_fiscal.id)])
            if budget_sbu_id:
                sbu_ids = [department.id for department in budget_sbu_id]
                domain = [('id', 'in', sbu_ids)]
        return domain

    department_id = fields.Many2one('hr.department', 'Department', readonly=True,
                                    default=lambda self: self.get_self_emp_dept_details())
    state = fields.Selection([
        ('draft', 'L1'),
        ('to_approve', 'L2'),
        ('approved', 'Finance'),
        ('cfo', 'Finance(CFO)'),
        ('confirm', 'Approval'),
        ('validate', 'Approved'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft', required=True, readonly=True, copy=False, track_visibility='always')
    fiscal_year_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', default=_default_financial_yr, required=True,
                                     track_visibility='always')
    sbu_project_budget_line_ids = fields.One2many('kw_sbu_project_budget_line', 'sbu_project_budget_id',
                                                  'SBU Project Budget Lines', copy=True)
    division_id = fields.Many2one('hr.department', 'Division', readonly=True,
                                  default=lambda self: self.get_self_emp_division_details())
    section_id = fields.Many2one('hr.department', 'Section', readonly=True, default=lambda self: self.get_emp_section())
    branch_id = fields.Many2one('kw_res_branch', 'Branch', readonly=True, default=lambda self: self.get_branch_id())
    rb_pending_at = fields.Char(string="Pending At")
    budget_department = fields.Many2one('kw_sbu_project_mapping', 'SBU Name', track_visibility='always',
                                        domain=_get_sbu_user)
    pending_at_ids = fields.Many2many('hr.employee', string='Pending at')
    revise_sbu_project_action_log_ids = fields.One2many('kw_revise_sbu_project_budget_action_log', 'project_budget_id',
                                                        'Revenue Budget Log')
    approver_head_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    revenue_revised_finance_approval_boolean = fields.Boolean()
    revenue_revised_approver_approval_boolean = fields.Boolean()
    revised_amount = fields.Float()
    revised_month = fields.Char()
    add_expense_line_hide_boolean = fields.Boolean()
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self._get_user_currency())
    finance_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    financecfo_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    approver_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    generate_seq_boolean = fields.Boolean(string='Generate Sequence Boolean')
    take_action_view_bool = fields.Boolean('Boolean', compute='_get_bool_enable')
    pending_since = fields.Datetime('Pending Since', default=datetime.now(), compute='_get_pending_since')

    @api.depends('state')
    def _get_pending_since(self):
        for rec in self:
            if rec.state:
                rec.pending_since = datetime.now()
            else:
                rec.pending_since = ''

    def _get_bool_enable(self):
        print(self.env.context)
        if self.env.context.get('take_action_view_bool'):
            self.take_action_view_bool = True
        else:
            self.take_action_view_bool = False

    # @api.constrains('fiscal_year_id', 'budget_department')
    # def _check_duplicate_sbu_budget(self):
    #     existing_record = self.search([
    #         ('fiscal_year_id', '=', self.fiscal_year_id.id),
    #         ('budget_department', '=', self.budget_department.id),
    #         # ('id', '!=', self.id),
    #         ('state', 'not in', ['cancel'])
    #     ])
    #     if existing_record:
    #         raise ValidationError("A record for this fiscal year already exists.")

    @api.constrains('fiscal_year_id', 'sbu_project_budget_line_ids')
    def _validate_budget_details(self):
        for budget in self:
            if budget.fiscal_year_id and not budget.sbu_project_budget_line_ids:
                raise ValidationError('Please add Budget details.')

    @api.model
    def _get_user_currency(self):
        if self.env.user.company_id:
            return self.env.user.company_id.currency_id.id

    @api.multi
    def get_self_emp_dept_details(self):
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.department_id

    @api.multi
    def get_self_emp_division_details(self):
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.division

    @api.multi
    def get_emp_section(self):
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.practise

    @api.multi
    def get_branch_id(self):
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.base_branch_id

    def get_boolean_all(self):
        for rec in self:
            rec.approver_head_boolean = True if rec.state == 'to_approve' and self.env.user.employee_ids.id in rec.budget_department.level_2_approver.ids else False
            rec.finance_revert_back_boolean = True if rec.state == 'approved' and self.env.user.has_group(
                'kw_budget.group_finance_kw_budget') else False
            rec.approver_revert_back_boolean = True if rec.state == 'confirm' and self.env.user.has_group(
                'kw_budget.group_approver_kw_budget') else False
            rec.financecfo_revert_back_boolean = True if rec.state == 'cfo' and self.env.user.has_group(
                'kw_budget.group_cfo_kw_budget') else False

    def apply_sbu_budget(self):
        for rec in self:
            if self.env.user.employee_ids.id in rec.budget_department.level_2_approver.ids:
                finance_group = self.env.ref(
                    'kw_budget.group_finance_kw_budget')
                finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                if not finance_users:
                    raise ValidationError("No users found in the finance group.")
                approver_ids = finance_users.mapped('employee_ids.id')
                rec.write({'state': 'approved',
                           'pending_at_ids': [(6, 0, approver_ids)]})
                for recc in rec.sbu_project_budget_line_ids:
                    recc.state = 'to_approve'
            else:
                approver_ids = rec.budget_department.level_2_approver.ids
                rec.write({'state': 'to_approve',
                           'pending_at_ids': [(6, 0, approver_ids)]})
                for recc in rec.sbu_project_budget_line_ids:
                    recc.state = 'to_approve'

    @api.multi
    def action_budget_confirm(self):
        finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
        finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
        if not finance_users:
            raise ValidationError("No users found in the finance group.")
        approver_ids = finance_users.mapped('employee_ids.id')
        for rec in self:
            rec.write({'state': 'approved',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.sbu_project_budget_line_ids:
                recc.state = 'to_approve'

    @api.multi
    def action_budget_validate(self):
        approver_group = self.env.ref(
            'kw_budget.group_approver_kw_budget')
        approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if not approver_users:
            raise ValidationError("No users found in the approver group.")
        approver_ids = approver_users.mapped('employee_ids.id')
        for rec in self:
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                for recc in rec.sbu_project_budget_line_ids:
                    if not recc.account_code_id:
                        raise ValidationError(f'Account Code is  not set for the expense {recc.head_of_expense}')
            rec.write({'state': 'confirm',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.sbu_project_budget_line_ids:
                recc.state = 'confirm'

    @api.multi
    def action_budget_validate_finance(self):
        approver_group = self.env.ref(
            'kw_budget.group_cfo_kw_budget')
        approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if not approver_users:
            raise ValidationError("No users found in the Finance CFO group.")
        approver_ids = approver_users.mapped('employee_ids.id')
        for rec in self:
            # if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            #     for recc in rec.sbu_project_budget_line_ids:
            #         if not recc.account_code_id:
            #             raise ValidationError(f'Account Code is  not set for the expense {recc.head_of_expense}')
            rec.write({'state': 'cfo',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.sbu_project_budget_line_ids:
                recc.state = 'confirm'

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_revenue_budget_validate(self):
        for rec in self:
            rec.write({'state': 'validate',
                       'add_expense_line_hide_boolean': True,
                       'pending_at_ids': [(6, 0, [])]})
            for recc in rec.sbu_project_budget_line_ids:
                recc.revised_button_hide_boolean = True
                recc.state = 'validate'

    def action_budget_revert_back(self):
        for rec in self:
            rec.write({'state': 'draft',
                       'add_expense_line_hide_boolean': False,
                       'pending_at_ids': [(6, 0, [])]})
            for recc in rec.sbu_project_budget_line_ids:
                recc.revised_button_hide_boolean = False
                recc.state = 'draft'

    def get_new_line_view(self):
        view_id = self.env.ref("kw_budget.kw_sbu_project_budget_form_new_line").id
        action = {
            'name': 'Add Budget Expense',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_sbu_project_budget',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {}
        }
        return action

    def open_capital_revise_wizard(self):
        return {
            'name': 'SBU Project Budget Budget Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'revised_sbu_project_budget_wizard',
            'view_id': self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id,
            'target': 'new',
            'context': {
                'default_sbu_project_budget_id': self.id,
                'kw_sbu_wizard': True
            },
        }

    def sbu_revised_add_line_submit(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_sbu_project_budget'].sudo().search([('id', '=', active_ids)])
        for rec in self.sbu_project_budget_line_ids:
            rec.sbu_project_budget_id = active_ids
            rec.state = 'to_approve'
            rec.edit_button_hide_boolean = True
            data.revenue_revised_finance_approval_boolean = True
            rec.finance_approved_button_boolean = True
            rec.revised_button_hide_boolean = False
            data.add_expense_line_hide_boolean = False
        self.unlink()

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # if self._context.get('take_action_sbu_budget'):
        user = self.env.user.employee_ids
        l2_ids = []
        l1_ids = []
        if self._context.get('take_action_sbu_budget'):
            l1_budget_obj = []
            l2_budget_obj = []
            budget_department_id = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_2_approver.id', '=', user.id)])
            if budget_department_id:
                if len(budget_department_id) == 1:
                    query = "select id from kw_sbu_project_budget where state = 'to_approve' and budget_department = " + str(
                        budget_department_id.id)
                if len(budget_department_id) > 1:
                    query = "select id from kw_sbu_project_budget where state = 'to_approve' and  budget_department in " + str(
                        tuple(budget_department_id.ids))
                self._cr.execute(query)
                ids = self._cr.fetchall()
                if ids:
                    l2_ids = [x[0] for x in ids]
            budget_department_id_l1 = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_sbu_project_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_sbu_project_budget where budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                finance_budget_obj = []
                cfo_budget_obj = []
                query = """
                                SELECT id
                                FROM kw_sbu_project_budget
                                WHERE state = 'confirm'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                    query = """
                                        SELECT id
                                        FROM kw_sbu_project_budget
                                        WHERE state = 'cfo'
                                    """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    cfo_budget_obj = [data[0] for data in lines_obj]

                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                        SELECT id
                                        FROM kw_sbu_project_budget
                                        WHERE state = 'approved'
                                    """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + cfo_budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                       count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                finance_budget_obj = []
                query = """
                                SELECT id
                                FROM kw_sbu_project_budget
                                WHERE state = 'cfo'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                        SELECT id
                                        FROM kw_sbu_project_budget
                                        WHERE state = 'approved'
                                    """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                       count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                                SELECT id
                                FROM kw_sbu_project_budget
                                WHERE state = 'approved'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                budget_obj = budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                       count=count, access_rights_uid=access_rights_uid)
            elif self.env.user.has_group('kw_budget.group_l2_kw_budget'):

                budget_obj = l2_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                       count=count, access_rights_uid=access_rights_uid)
            else:
                budget_obj = l1_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                       count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('take_action_view_bool'):
            budget_department_id_l1 = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_sbu_project_budget where state = 'validate' and  budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_sbu_project_budget where state = 'validate' and budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                   count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('project_budget_create'):
            l1_ids = []
            budget_department_id_l1 = self.env['kw_sbu_project_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_sbu_project_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_sbu_project_budget where budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                   count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('view_status_project_budget'):
            if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += ['|', ('create_uid', '=', self.env.user.id), '&',
                         ('budget_department.level_2_approver', 'in', self.env.user.employee_ids.ids),
                         ('state', 'not in', ['draft'])]
            elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_approver_kw_budget') or self.env.user.has_group(
                'kw_budget.group_manager_kw_budget'):
                args += [('state', 'not in', ['draft'])]

        return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                               count=count,
                                                               access_rights_uid=access_rights_uid)

    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('take_action_sbu_budget'):
    #         if  self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', '&',('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|',('state', 'in', ['approved', 'confirm']), ('revenue_revised_finance_approval_boolean', '=', True)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args += [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #
    #
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #             args += ['|', '&', ('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|', ('state', 'in', ['confirm']), ('revenue_revised_approver_approval_boolean', '=', True)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args += [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget') and self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', '|',('state', 'in', ['approved', 'confirm']), ('revenue_revised_finance_approval_boolean', '=', True), '|',('state', 'in', ['approved', 'confirm']), ('revenue_revised_finance_approval_boolean', '=', True)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args += [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             args += [('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args = [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|', ('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|',('state', 'in', ['approved', 'confirm']), ('revenue_revised_finance_approval_boolean', '=', True)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args += [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #             args += ['|', ('state', 'in', ['confirm']), ('revenue_revised_approver_approval_boolean', '=', True)]
    #             if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #                 args += [('state', 'in', ['cfo']),
    #                          ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #             args += [('state', 'in', ['cfo']),
    #                      ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_manager_kw_budget'):
    #             return []
    #     elif self._context.get('view_status_project_budget'):
    #         if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             args += ['|', ('create_uid', '=', self.env.user.id), '&', ('budget_department.level_2_approver', 'in', self.env.user.employee_ids.ids), ('state', 'not in', ['draft'])]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
    #             args += [('state', 'not in', ['draft'])]
    #
    #     return super(AccountingSBUProjectBudget, self)._search(args, offset=offset, limit=limit, order=order, count=count,
    #                                                         access_rights_uid=access_rights_uid)
    def action_project_budget_generate_id(self):
        # if not self.generate_seq_boolean:
        params = self.env['ir.config_parameter'].sudo()
        count = params.get_param('id_count_project')

        line_data = self.env['kw_sbu_project_budget_line'].sudo().search(
            [('state', '=', 'validate'), ('sbu_project_budget_id.fiscal_year_id', '=', self.fiscal_year_id.id)])
        sequence_map = {}
        for rec in line_data:
            sbu_name = rec.sbu_project_budget_id.budget_department
            if sbu_name not in sequence_map:
                sequence_map[sbu_name] = []
            sequence_map[sbu_name].append(rec)
        sorted_departments = sorted(sequence_map.keys())
        sequence_number = int(count) + 1
        for department_name in sorted_departments:
            for rec in sequence_map[department_name]:
                if rec.sequence_ref:
                    sequence_number_copy = rec.sequence_ref
                    if rec.id_revise_bool:
                        sequence_number_copy = rec.sequence_ref
                        if 'R' not in rec.sequence_ref:
                            sequence_number_copy = 'R' + str(rec.sequence_ref)
                        if rec.id_new_line_bool:
                            sequence_number_copy = sequence_number_copy
                            if 'A' not in rec.sequence_ref:
                                sequence_number_copy = 'A' + str(sequence_number_copy)

                if not rec.sequence_ref:
                    sequence_number_copy = sequence_number
                    if rec.id_new_line_bool:
                        sequence_number_copy = 'A-' + 'P' + str(sequence_number_copy)
                        if rec.id_revise_bool:
                            sequence_number_copy = 'R-' + str(sequence_number_copy)
                        params.set_param('id_count_project', sequence_number)
                        sequence_number += 1

                    elif rec.id_revise_bool:
                        sequence_number_copy = 'R-' + 'P' + str(sequence_number_copy)

                        params.set_param('id_count_project', sequence_number)
                        sequence_number += 1
                    else:
                        seq = sequence_number_copy
                        sequence_number_copy = 'P' + sequence_number_copy

                        params.set_param('id_count_project', seq)
                        sequence_number += 1
                rec.sequence_ref = sequence_number_copy

    def print_project_report(self):
        '''
        this function is used to print the XLXS report
        '''

        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'Project Budget.xlsx')
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format({'num_format': 'd-m-yyyy',
                                           'align': 'center',
                                           'valign': 'vcenter'})

        style_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_data = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True})
        style_data2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'text_wrap': True})
        style_data3 = workbook.add_format({
            'border': 1,
            'align': 'left',
            'bold': 1,
            'text_wrap': True})
        style_total = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_color': 'white',
            'valign': 'vcenter'})
        style_header2.set_text_wrap()
        style_header.set_font_size(18)
        # style_header.set_text_wrap()
        style_header.set_bg_color('#95DDF7')
        style_header.set_font_name('Agency FB')
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        # style_data.set_text_wrap()
        style_data.set_font_name('Agency FB')
        style_data2.set_font_size(12)
        style_data2.set_font_name('Agency FB')
        style_data2.set_bg_color('#95DDF7')
        style_data3.set_font_size(12)
        style_data3.set_font_name('Agency FB')
        style_data3.set_bg_color('#6dd45c')
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_total.set_border(style=2)
        date_format.set_font_size(12)
        # date_format.set_bg_color('#DBF0F6')
        date_format.set_font_name('Agency FB')
        date_format.set_border(style=2)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('#108fbb')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet('Treasury Budget Report')
        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 8)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 30)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 10)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 10)
        worksheet.set_column(13, 13, 10)
        worksheet.set_column(14, 14, 10)
        worksheet.set_column(15, 15, 15)
        worksheet.set_column(16, 16, 16)
        worksheet.set_row(0, 25)
        worksheet.set_row(1, 50)
        row, col = 0, 0
        worksheet.merge_range(row, col, row, col + 22, "Project Budget", style_header)
        row += 1
        worksheet.write(row, col, 'sr.No ', style_header2)
        worksheet.write(row, col + 1, 'Order Type', style_header2)
        worksheet.write(row, col + 2, 'Project Name', style_header2)
        worksheet.write(row, col + 3, 'Work Order Code', style_header2)
        worksheet.write(row, col + 4, 'Opportunity Name', style_header2)
        worksheet.write(row, col + 5, 'Client Name', style_header2)
        worksheet.write(row, col + 6, 'Order Value', style_header2)
        worksheet.write(row, col + 7, 'Expenses/Income', style_header2)
        worksheet.write(row, col + 8, 'Particular', style_header2)
        worksheet.write(row, col + 9, 'Category ', style_header2)
        worksheet.write(row, col + 10, 'April ', style_header2)
        worksheet.write(row, col + 11, 'May ', style_header2)
        worksheet.write(row, col + 12, 'June ', style_header2)
        worksheet.write(row, col + 13, 'July ', style_header2)
        worksheet.write(row, col + 14, 'August ', style_header2)
        worksheet.write(row, col + 15, 'September ', style_header2)
        worksheet.write(row, col + 16, 'October ', style_header2)
        worksheet.write(row, col + 17, 'November ', style_header2)
        worksheet.write(row, col + 18, 'December ', style_header2)
        worksheet.write(row, col + 19, 'January ', style_header2)
        worksheet.write(row, col + 20, 'Feburary ', style_header2)
        worksheet.write(row, col + 21, 'March ', style_header2)
        worksheet.write(row, col + 22, 'Total Amount', style_header2)

        if self:
            apr, may, june, july, aug, sep, oct, nov, dec, jan, feb, mar, total = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

            for lines in self.sbu_project_budget_line_ids:
                row += 1
                print(lines, 'single linee')
                worksheet.write(row, col, row, style_data)
                worksheet.write(row, col + 1, lines.work_order_type, style_data)
                worksheet.write(row, col + 2, lines.project_id.wo_name or '', style_data)
                worksheet.write(row, col + 3, lines.project_code, style_data)
                worksheet.write(row, col + 4, lines.opportunity_name, style_data)
                worksheet.write(row, col + 5, lines.client, style_data)
                worksheet.write(row, col + 6, lines.order_value, style_data)
                worksheet.write(row, col + 7, lines.head_expense_type or '', style_data)
                worksheet.write(row, col + 8, lines.head_of_expense or '', style_data)
                worksheet.write(row, col + 9, lines.category_id.name, style_data)
                worksheet.write(row, col + 10, lines.apr_budget, style_data)
                worksheet.write(row, col + 11, lines.may_budget, style_data)
                worksheet.write(row, col + 12, lines.jun_budget, style_data)
                worksheet.write(row, col + 13, lines.jul_budget or '', style_data)
                worksheet.write(row, col + 14, lines.aug_budget or '', style_data)
                worksheet.write(row, col + 15, lines.sep_budget, style_data)
                worksheet.write(row, col + 16, lines.oct_budget, style_data)
                worksheet.write(row, col + 17, lines.nov_budget, style_data)
                worksheet.write(row, col + 18, lines.dec_budget, style_data)
                worksheet.write(row, col + 19, lines.jan_budget, style_data)
                worksheet.write(row, col + 20, lines.feb_budget, style_data)
                worksheet.write(row, col + 21, lines.mar_budget, style_data)
                worksheet.write(row, col + 22, lines.total_amount, style_data2)
                apr += lines.apr_budget
                may += lines.may_budget
                june += lines.jun_budget
                july += lines.jul_budget
                aug += lines.aug_budget
                sep += lines.sep_budget
                oct += lines.oct_budget
                nov += lines.nov_budget
                dec += lines.dec_budget
                jan += lines.jan_budget
                feb += lines.feb_budget
                mar += lines.mar_budget
                total += lines.total_amount
            row += 1
            worksheet.write(row, col + 10, apr, style_data3)
            worksheet.write(row, col + 11, may, style_data3)
            worksheet.write(row, col + 12, june, style_data3)
            worksheet.write(row, col + 13, july or '', style_data3)
            worksheet.write(row, col + 14, aug or '', style_data3)
            worksheet.write(row, col + 15, sep, style_data3)
            worksheet.write(row, col + 16, oct, style_data3)
            worksheet.write(row, col + 17, nov, style_data3)
            worksheet.write(row, col + 18, dec, style_data3)
            worksheet.write(row, col + 19, jan, style_data3)
            worksheet.write(row, col + 20, feb, style_data3)
            worksheet.write(row, col + 21, mar, style_data3)
            worksheet.write(row, col + 22, total, style_data3)

        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "Project Budget.xlsx"
        out_wizard = self.env['budget.xlsx.output'].create({'name': name,
                                                            'xls_output': base64.encodebytes(data)})
        view_id = self.env.ref('kw_budget.budget_xlsx_output_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'budget.xlsx.output',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }


class SBUProjectBudgetLine(models.Model):
    _name = 'kw_sbu_project_budget_line'
    _rec_name = 'head_of_expense'

    head_of_expense = fields.Char('Particular', required=True)
    account_code_id = fields.Many2one('account.account', 'Account code')
    work_order_type = fields.Selection([
        ('work_order', 'Work Order'),
        ('opportunity', 'Opportunity'),
    ], default='work_order', string='Order Type', track_visibility='always')
    opportunity_name = fields.Char(string='Opportunity Name')
    order_code = fields.Char('Order Code', related='order_id.crm_id.code', store=True)
    project_code = fields.Char('Work Order Code', related='project_id.wo_code', store=True)
    client = fields.Char(string='Client Name')
    order_id = fields.Many2one('project.project', 'Order Name')
    project_id = fields.Many2one('kw_project_budget_master_data', 'Project Name')
    order_value = fields.Char(string='Order Value')
    category_id = fields.Many2one('kw_sbu_project_category_master', string='Category', required=True)
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount')
    sbu_project_budget_id = fields.Many2one('kw_sbu_project_budget', 'project Budget')
    head_expense_type = fields.Selection(string='Expenses/Income',
                                         selection=[('Income', 'Income'), ('Expenses', 'Expenses')], required=True)
    revise_sbu_project_action_log_ids = fields.One2many('kw_revise_sbu_project_budget_action_log',
                                                        'sbu_project_budget_line_id', 'Revenue Budget Log')
    finance_approved_button_boolean = fields.Boolean()
    approver_approved_button_boolean = fields.Boolean()
    approver_reverted_button_boolean = fields.Boolean()
    revised_button_hide_boolean = fields.Boolean()
    edit_button_hide_boolean = fields.Boolean()
    # actual_amount = fields.Float('Expenses Amount', compute="_compute_practical_amount", readonly=True)
    billing_amount = fields.Float('Billing Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('cancel', 'Cancelled'),
        ('re_apply', 'Reapply'),
        ('re_f_approved', 'ReApproved')
    ], 'Status', default='draft', required=True, readonly=True, copy=False, track_visibility='always')
    currency_id = fields.Many2one('res.currency', related='sbu_project_budget_id.currency_id')
    sequence_ref = fields.Char(string='ID')
    hide_split_button_boolean = fields.Boolean(default=False)
    wizard_id = fields.Many2one('revised_sbu_project_budget_wizard', string='Wizard')
    id_revise_bool = fields.Boolean(default=False)
    id_new_line_bool = fields.Boolean(default=False)

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                  'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget',
                  'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget')
    def calulate_total_planed_amount(self):
        if not self._context.get('non_treasury_budget'):
            # for rec in self:
            self.total_amount = False
            self.total_amount = self.apr_budget + self.may_budget + self.jun_budget + \
                                self.jul_budget + self.aug_budget + self.sep_budget + \
                                self.oct_budget + self.nov_budget + self.dec_budget + \
                                self.jan_budget + self.feb_budget + self.mar_budget

    def approve_revised_revenue_budget(self):
        for rec in self:
            log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                [('sbu_project_budget_line_id', '=', rec.sbu_project_budget_id.id),
                 ('head_of_expense', '=', rec.head_of_expense),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.state = 're_f_approved'
                    rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state in ['to_approve', 're_apply']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_finance_approval_boolean = False  # record for search view
                        # rec.revenue_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view
                        approver_group = self.env.ref(
                            'kw_budget.group_approver_kw_budget')
                        approver_group_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
                        if not approver_group_users:
                            raise ValidationError("No users found in the approver group.")
                        approver_ids = approver_group_users.mapped('employee_ids.id')
                        rec.sbu_project_budget_id.pending_at_ids = [(6, False, approver_ids)]
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Finance Approved',
                        'approve_date': date.today(),
                        'revise_budget_status': 'approved_by_finance',
                    })

                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    data = self.env['revised_sbu_project_budget_wizard'].search([('project_expense_id', '=', rec.id)],
                                                                                limit=1)
                    rec.head_of_expense = data.head_of_expense
                    # rec.remark = data.remarks
                    rec.state = 'validate'
                    month_mapping = {
                        'April': 'apr_budget',
                        'May': 'may_budget',
                        'Jun': 'jun_budget',
                        'July': 'jul_budget',
                        'August': 'aug_budget',
                        'September': 'sep_budget',
                        'October': 'oct_budget',
                        'November': 'nov_budget',
                        'December': 'dec_budget',
                        'January': 'jan_budget',
                        'February': 'feb_budget',
                        'March': 'mar_budget',
                    }
                    total_amountt = 0
                    for recc in data.revised_amount_ids:
                        total_amountt += recc.revised_amount
                        month_field = month_mapping.get(recc.month_revies)
                        if month_field:
                            setattr(rec, month_field, getattr(rec, month_field) + recc.revised_amount)
                    rec.total_amount += total_amountt
                    data.revised_amount_ids.unlink()
                    data.unlink()
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = False
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Approved',
                        'approve_date': date.today(),
                        'total_amount': rec.total_amount,
                        'revise_budget_status': 'approved_by_approver',
                    })
            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    if not rec.account_code_id:
                        raise ValidationError('Please set Account Code.')
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.state = 'confirm'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = True
                    rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = True  # for search method
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state in ['to_approve', 're_apply']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_finance_approval_boolean = False  # for search method
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'validate'
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.sbu_project_budget_id.add_expense_line_hide_boolean = True
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = False  # for search method

    def reject_sbu_project_budget(self):
        # log_record = self.env['kw_revise_revenue_budget_action_log'].search([('revenue_budget_line_id', '=', self.id),('approved','=',False)],limit=1)
        for rec in self:
            log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                [('sbu_project_budget_line_id', '=', rec.id),
                 ('head_of_expense', '=', rec.head_of_expense),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.state = 'validate'
                    rec.approver_approved_button_boolean = False
                    rec.finance_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    val = []

                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state == 're_apply':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_finance_approval_boolean = False  # record for search view
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'revise_budget_status': 'rejected_by_finance',
                    })
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    data = self.env['revised_sbu_project_budget_wizard'].search([('project_expense_id', '=', rec.id)],
                                                                                limit=1)
                    rec.state = 'validate'
                    data.revised_amount_ids.unlink()
                    data.unlink()
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state == 're_f_approved':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = False
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'total_amount': rec.total_amount,
                        'revise_budget_status': 'rejected_by_approver',
                    })
            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.state = 'cancel'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state == 'to_approve':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_finance_approval_boolean = False  # for search method
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = False  # for search method
                        rec.sbu_project_budget_id.add_expense_line_hide_boolean = True
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'cancel'
                    rec.sbu_project_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    val = []
                    for dataa in rec.sbu_project_budget_id.sbu_project_budget_line_ids:
                        if dataa.state == 'confirm':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.sbu_project_budget_id.revenue_revised_approver_approval_boolean = False  # for search method
                        rec.sbu_project_budget_id.add_expense_line_hide_boolean = True

    def edit_budget_button(self):
        for rec in self:
            data = self.env['revised_sbu_project_budget_wizard'].sudo().search([('project_expense_id', '=', rec.id)],
                                                                               limit=1)
            default_revised_amount_ids = [
                {'month_revies': item.month_revies, 'revised_amount': item.revised_amount}
                for item in data.revised_amount_ids
            ]
            return {
                'name': 'Revised SBU Project Budget Wizard',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'revised_sbu_project_budget_wizard',
                'view_id': self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_project_expense_id': rec.id,
                    'default_head_of_expense': rec.head_of_expense,
                    # 'default_expense_type': rec.expense_type,
                    'default_revised_amount_ids': default_revised_amount_ids,
                },
            }


class RevisedSBUWizard(models.Model):
    _name = 'revised_sbu_project_budget_wizard'
    _description = 'revised button wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sbu_project_budget_id'

    revised_amount = fields.Float(string='Revise Amount')
    month_revies = fields.Selection(string="Month of Revies",
                                    selection=[('April', 'Apr'), ('May', 'May'), ('Jun', 'Jun'),
                                               ('July', 'July'), ('August', 'Aug'),
                                               ('September', 'Sep'), ('October', 'Oct'),
                                               ('November', 'Nov'), ('December', 'Dec'), ('January', 'Jan'),
                                               ('February', 'Feb'), ('March', 'Mar')])
    project_expense_id = fields.Many2one('kw_sbu_project_budget_line')
    revised_amount_ids = fields.One2many('revised_sbu_project_budget_data', 'wizard_id', string='Revised Amounts')
    head_of_expense = fields.Char('Particular')
    order_code = fields.Many2one('project.project', 'Order code')

    sbu_project_budget_line_ids = fields.One2many('kw_sbu_project_budget_line', 'wizard_id',
                                                  'SBU Project Budget Lines', copy=True)
    existing_sbu_project_budget_line_ids = fields.One2many('kw_sbu_project_line_wizard', 'wizard_id',
                                                           'SBU Project Budget Lines')
    pending_at = fields.Selection(string="Status",
                                  selection=[('L1', ''), ('L2', 'L2'), ('Finance', 'Finance'), ('Approver', 'Approver'),
                                             ('Validate', 'Validate'),
                                             ('Cancel', 'Cancel')], default="L1", track_visibility='onchange')
    budget_department = fields.Char('Budget For')
    branch_id = fields.Char('Branch')
    for_new_line = fields.Boolean('For New Budget Line')
    for_revise_line = fields.Boolean('For Revise Budget Line')
    sbu_project_budget_id = fields.Many2one('kw_sbu_project_budget', string="SBU Project Budget")
    pending_at = fields.Selection(string="Status",
                                  selection=[('L1', ''), ('L2', 'L2'), ('Finance', 'Finance'), ('cfo', 'Finance(CFO)'),
                                             ('Approver', 'Approver'),
                                             ('Validate', 'Validate'),
                                             ('Cancel', 'Cancel')], default="L1", track_visibility='onchange')
    department_id = fields.Char('Department')

    show_apply = fields.Boolean('Show Apply', compute='get_boolean_all')
    pending_since = fields.Datetime('Pending Since', default=datetime.now(), compute='_get_pending_since')

    @api.depends('pending_at')
    def _get_pending_since(self):
        for rec in self:
            if rec.pending_at:
                rec.pending_since = datetime.now()
            else:
                rec.pending_since = ''

    def get_boolean_all(self):
        for rec in self:
            rec.show_apply = True if rec.pending_at == 'L1' and self.env.user.employee_ids.id in rec.sbu_project_budget_id.budget_department.level_1_approver.ids else False

    def apply_l1(self):
        if self.pending_at == 'L1':
            self.pending_at = 'L2'

    @api.onchange('capital_budget_id')
    def onchnage_sbu_project_budget_details(self):
        if self.sbu_project_budget_id:
            self.budget_department = self.sbu_project_budget_id.budget_department.sbu_id.name
            self.branch_id = self.sbu_project_budget_id.branch_id.name
            self.department_id = self.sbu_project_budget_id.department_id.name

    @api.onchange('revised_amount_ids')
    def _onchange_sbu_project_existing_lines(self):
        if self.revised_amount_ids:
            new_lines = []
            self.existing_sbu_project_budget_line_ids = [(5, 0, 0)]
            for rec in self.revised_amount_ids:
                if rec.project_expense_id:
                    rec.client = rec.project_expense_id.client
                    rec.order_value = rec.project_expense_id.order_value
                    rec.head_expense_type = rec.project_expense_id.head_expense_type
                    rec.category_id = rec.project_expense_id.category_id.id
                    new_lines.append((0, 0, {
                        "work_order_type": rec.project_expense_id.work_order_type,
                        "project_id": rec.project_expense_id.project_id.id,
                        "project_code": rec.project_expense_id.project_code,
                        "opportunity_name": rec.project_expense_id.opportunity_name,
                        "order_value": rec.project_expense_id.order_value,
                        "client": rec.project_expense_id.client,
                        "head_expense_type": rec.project_expense_id.head_expense_type,
                        "head_of_expense": rec.project_expense_id.head_of_expense,
                        "category_id": rec.project_expense_id.category_id.id,
                        "apr_budget": rec.project_expense_id.apr_budget,
                        "may_budget": rec.project_expense_id.may_budget,
                        "jun_budget": rec.project_expense_id.jun_budget,
                        "jul_budget": rec.project_expense_id.jul_budget,
                        "aug_budget": rec.project_expense_id.aug_budget,
                        "sep_budget": rec.project_expense_id.sep_budget,
                        "oct_budget": rec.project_expense_id.oct_budget,
                        "nov_budget": rec.project_expense_id.nov_budget,
                        "dec_budget": rec.project_expense_id.dec_budget,
                        "jan_budget": rec.project_expense_id.jan_budget,
                        "feb_budget": rec.project_expense_id.feb_budget,
                        "mar_budget": rec.project_expense_id.mar_budget,
                        "total_amount": rec.project_expense_id.total_amount,

                    }))
            self.existing_sbu_project_budget_line_ids = new_lines

    def format_revised_amounts(self, line_obj):
        format_rev_amts_list = []
        format_rev_amts = ''
        for rec in line_obj:
            if rec.apr_budget:
                format_rev_amts += f"{'April'} : {str(rec.apr_budget)} "
            if rec.may_budget:
                format_rev_amts += f"{'May'} : {str(rec.may_budget)} "
            if rec.jun_budget:
                format_rev_amts += f"{'June'} : {str(rec.jun_budget)} "
            if rec.jul_budget:
                format_rev_amts += f"{'July'} : {str(rec.jul_budget)} "
            if rec.aug_budget:
                format_rev_amts += f"{'August'} : {str(rec.aug_budget)} "
            if rec.sep_budget:
                format_rev_amts += f"{'September'} : {str(rec.sep_budget)} "
            if rec.oct_budget:
                format_rev_amts += f"{'October'} : {str(rec.oct_budget)} "
            if rec.nov_budget:
                format_rev_amts += f"{'November'} : {str(rec.nov_budget)} "
            if rec.dec_budget:
                format_rev_amts += f"{'December'} : {str(rec.dec_budget)} "
            if rec.jan_budget:
                format_rev_amts += f"{'January'} : {str(rec.jan_budget)} "
            if rec.feb_budget:
                format_rev_amts += f"{'April'} : {str(rec.feb_budget)} "
            if rec.mar_budget:
                format_rev_amts += f"{'March'} : {str(rec.mar_budget)} "
            format_rev_amts_list.append(format_rev_amts)
        return ', '.join(format_rev_amts_list)

    @api.onchange('project_expense_id')
    def get_value(self):
        self.head_of_expense = self.project_expense_id.head_of_expense
        # self.expense_type = self.revenue_expense_id.expense_type

    def revenue_sbu_project_amount_submit(self):
        data = self.env['revised_sbu_project_budget_wizard'].sudo().search(
            [('project_expense_id', '=', self.project_expense_id.id)]) - self
        data.unlink()

        for rec in self:
            rec.project_expense_id.sbu_project_budget_id.revenue_revised_finance_approval_boolean = True
            rec.project_expense_id.finance_approved_button_boolean = True
            rec.project_expense_id.revised_button_hide_boolean = False
            rec.project_expense_id.edit_button_hide_boolean = True
            rec.project_expense_id.state = 're_apply'
            # rec.revenue_expense_id.revenue_budget_id.revised_amount = self.revised_amount
            # rec.revenue_expense_id.revenue_budget_id.revised_month = self.month_revies
            finance_group = self.env.ref(
                'kw_budget.group_finance_kw_budget')
            finance_group_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
            if not finance_group_users:
                raise ValidationError("No users found in the finance group.")
            finance_ids = finance_group_users.mapped('employee_ids.id')
            format_rev_amts = self.format_revised_amounts()
            log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                [('sbu_project_budget_line_id', '=', rec.project_expense_id.id),
                 ('head_of_expense', '=', rec.head_of_expense),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if log_data:
                log_data.write({
                    'head_of_expense': rec.project_expense_id.head_of_expense,
                    'revised_amount': format_rev_amts,
                    'total_amount': rec.project_expense_id.total_amount,
                    'approver_by': self.env.user.employee_ids.name,
                    'revenue_budget_line_id': rec.project_expense_id.id,
                    'state': 'Applied',
                    'revise_budget_status': 'applied',
                })
            else:
                rec.project_expense_id.sbu_project_budget_id.write({
                    'revise_sbu_project_action_log_ids': [[0, 0, {
                        'head_of_expense': rec.project_expense_id.head_of_expense,
                        'revised_amount': format_rev_amts,
                        'total_amount': rec.project_expense_id.total_amount,
                        'approver_by': self.env.user.employee_ids.name,
                        'revenue_budget_line_id': rec.project_expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    }]],
                    'pending_at_ids': [(6, 0, finance_ids)]
                })

    def open_take_action_sbu_budget_lines(self):
        ''' function is used to redirect revise/ADD revenue Budget lines list, form view. '''
        res = self.env.ref('kw_budget.action_revised_sbu_project_budget_wizard').read()[0]
        res['context'] = {'create': False, 'edit': False}
        user = self.env.user.employee_ids
        budget_department_id = self.env['kw_sbu_project_mapping'].search([
            ('level_2_approver.id', '=', user.id)])
        if budget_department_id:
            if len(budget_department_id) == 1:
                query = "select id from kw_sbu_project_budget where budget_department = " + str(
                    budget_department_id.id)
            if len(budget_department_id) > 1:
                query = "select id from kw_sbu_project_budget where budget_department in " + str(
                    tuple(budget_department_id.ids))
            self._cr.execute(query)
            ids = self._cr.fetchall()
            if ids:
                budget_obj = self.env['revised_sbu_project_budget_wizard'].search(
                    [('sbu_project_budget_id', 'in', ids), ('pending_at', '=', 'L2')])
                res['views'] = [(self.env.ref('kw_budget.view_revised_sbu_project_budget_wizard_tree').id, 'list'),
                                (self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id, 'form')]
                res['domain'] = [('id', 'in', budget_obj.ids)]
                res['context'] = {'create': False, 'edit': True}

        if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            budget_obj = self.env['revised_sbu_project_budget_wizard'].search(
                [('pending_at', '=', 'Finance')])
            res['views'] = [(self.env.ref('kw_budget.view_revised_sbu_project_budget_wizard_tree').id, 'list'),
                            (self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id, 'form')]
            res['domain'] = [('id', 'in', budget_obj.ids)]
            res['context'] = {'create': False, 'edit': True}

        if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
            budget_obj = self.env['revised_sbu_project_budget_wizard'].search(
                [('pending_at', '=', 'Approver')])
            res['views'] = [(self.env.ref('kw_budget.view_revised_sbu_project_budget_wizard_tree').id, 'list'),
                            (self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id, 'form')]
            res['domain'] = [('id', 'in', budget_obj.ids)]

        if self.env.user.has_group('kw_budget.group_manager_kw_budget'):
            budget_obj = self.env['revised_sbu_project_budget_wizard'].search(
                [('pending_at', '=', 'Approver')])
            res['views'] = [(self.env.ref('kw_budget.view_revised_sbu_project_budget_wizard_tree').id, 'list'),
                            (self.env.ref('kw_budget.revised_amount_sbu_wizard_form').id, 'form')]
            res['domain'] = [('id', 'in', budget_obj.ids)]

        # else:
        #     res['context'] = {'create': False, 'edit': True}
        #     res['domain'] = [('create_uid', '=', self.env.user.id)]
        #

        # else:
        #     res = self.env['ir.actions.act_window'].for_xml_id('gts_coe_incubatee', 'action_incubatee_showcase')
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        l2_ids = []
        l1_ids = []
        l1_budget_obj = []
        l2_budget_obj = []
        user = self.env.user.employee_ids
        budget_department_id = self.env['kw_sbu_project_mapping'].sudo().search([
            ('level_2_approver.id', '=', user.id)])
        if budget_department_id:
            if len(budget_department_id) == 1:
                query = "select id from kw_sbu_project_budget where budget_department = " + str(
                    budget_department_id.id)
            if len(budget_department_id) > 1:
                query = "select id from kw_sbu_project_budget where budget_department in " + str(
                    tuple(budget_department_id.ids))
            self._cr.execute(query)
            ids = self._cr.fetchall()
            if ids:
                l2_ids = [x[0] for x in ids]
                query = """
                            SELECT id
                            FROM revised_sbu_project_budget_wizard
                            WHERE sbu_project_budget_id IN %s
                            AND pending_at = 'L2'
                        """
                self._cr.execute(query, (tuple(l2_ids),))
                lines_obj = self._cr.fetchall()
                l2_budget_obj = [data[0] for data in lines_obj]
        budget_department_id_l1 = self.env['kw_sbu_project_mapping'].sudo().search([
            ('level_1_approver.id', '=', user.id)])
        if budget_department_id_l1:
            if len(budget_department_id_l1) == 1:
                l1query = "select id from kw_sbu_project_budget where budget_department = " + str(
                    budget_department_id_l1.id)
            if len(budget_department_id_l1) > 1:
                l1query = "select id from kw_sbu_project_budget where budget_department in " + str(
                    tuple(budget_department_id_l1.ids))
            self._cr.execute(l1query)
            l1_ids = self._cr.fetchall()
            if l1_ids:
                l1_ids = [x[0] for x in l1_ids]
                query = """
                            SELECT id
                            FROM revised_sbu_project_budget_wizard
                            WHERE sbu_project_budget_id IN %s
                        """
                self._cr.execute(query, (tuple(l1_ids),))
                lines_obj = self._cr.fetchall()
                l1_budget_obj = [data[0] for data in lines_obj]
        if self.env.user.has_group('kw_budget.group_manager_kw_budget'):
            query = """
                                    SELECT id
                                    FROM revised_sbu_project_budget_wizard
                                """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            args = [('id', 'in', budget_obj)]
            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
            finance_budget_obj = []
            cfo_budget_obj = []

            query = """
                        SELECT id
                        FROM revised_sbu_project_budget_wizard
                        WHERE pending_at = 'Approver'
                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                                SELECT id
                                FROM revised_sbu_project_budget_wizard
                                WHERE pending_at = 'Finance'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                finance_budget_obj = [data[0] for data in lines_obj]

            if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                query = """
                                SELECT id
                                FROM revised_sbu_project_budget_wizard
                                WHERE pending_at = 'cfo'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                cfo_budget_obj = [data[0] for data in lines_obj]

            budget_obj = budget_obj + finance_budget_obj + cfo_budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
            finance_budget_obj = []

            query = """
                        SELECT id
                        FROM revised_sbu_project_budget_wizard
                        WHERE pending_at = 'cfo'
                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]

            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                                SELECT id
                                FROM revised_sbu_project_budget_wizard
                                WHERE pending_at = 'Finance'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                finance_budget_obj = [data[0] for data in lines_obj]
            budget_obj = budget_obj + finance_budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            query = """
                        SELECT id
                        FROM revised_sbu_project_budget_wizard
                        WHERE pending_at = 'Finance'
                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            budget_obj = budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_l2_kw_budget'):
            domain_ids = []
            domain_ids = l2_budget_obj + l1_budget_obj
            args = [('id', 'in', domain_ids)]

            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)
        else:
            domain_ids = l1_budget_obj
            args = [('id', 'in', domain_ids)]
            return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)
        return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                     count=count, access_rights_uid=access_rights_uid)

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     user = self.env.user.employee_ids
    #     budget_department_id = self.env['kw_sbu_project_mapping'].search([
    #         ('level_2_approver.id', '=', user.id)])
    #     if budget_department_id:
    #         if len(budget_department_id) == 1:
    #             query = "select id from kw_sbu_project_budget where budget_department = " + str(
    #                 budget_department_id.id)
    #         if len(budget_department_id) > 1:
    #             query = "select id from kw_sbu_project_budget where budget_department in " + str(
    #                 tuple(budget_department_id.ids))
    #         self._cr.execute(query)
    #         ids = self._cr.fetchall()
    #         if ids:
    #             id_list = tuple([id[0] for id in ids])  # Extracting the IDs and making them a tuple
    #             query = """
    #                         SELECT id
    #                         FROM revised_sbu_project_budget_wizard
    #                         WHERE sbu_project_budget_id IN %s
    #                         AND pending_at = 'L2'
    #                     """
    #             self._cr.execute(query, (id_list,))
    #             lines_obj = self._cr.fetchall()
    #             args += [('id', 'in', lines_obj)]
    #     if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #         query = """
    #                                     SELECT id
    #                                     FROM revised_sbu_project_budget_wizard
    #                                     WHERE pending_at = 'Finance'
    #                                 """
    #         self._cr.execute(query)
    #         budget_obj = self._cr.fetchall()
    #         args += [('id', 'in', budget_obj)]
    #     if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #         query = """
    #                                                 SELECT id
    #                                                 FROM revised_sbu_project_budget_wizard
    #                                                 WHERE pending_at = 'Approver'
    #                                             """
    #         self._cr.execute(query)
    #         budget_obj = self._cr.fetchall()
    #         args += [('id', 'in', budget_obj)]
    #
    #     return super(RevisedSBUWizard, self)._search(args, offset=offset, limit=limit, order=order,
    #                                                     count=count, access_rights_uid=access_rights_uid)

    def confirm_apply(self):
        self.onchnage_sbu_project_budget_details()
        if self.pending_at == 'L1':
            self.pending_at = 'L2'
        if self.revised_amount_ids and self.for_revise_line:

            for rec in self.revised_amount_ids:
                line_changes = self.format_revised_amounts(rec)
                log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                    [('sbu_project_budget_line_id', '=', rec.project_expense_id.id),
                     ('head_of_expense', '=', rec.project_expense_id.head_of_expense),
                     ('revise_budget_status', 'in', ['applied', 'L2', 'approved_by_finance'])])
                if log_data:
                    log_data.write({
                        'head_of_expense': rec.project_expense_id.head_of_expense,
                        'revised_amount': line_changes,
                        'total_amount': rec.project_expense_id.total_amount,
                        'approver_by': self.env.user.employee_ids.name,
                        'sbu_project_budget_line_id': rec.project_expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    })
                if not log_data:
                    d = self.env['kw_revise_sbu_project_budget_action_log'].sudo().create({
                        'head_of_expense': rec.project_expense_id.head_of_expense,
                        'revised_amount': line_changes,
                        'total_amount': rec.project_expense_id.total_amount,
                        'approver_by': self.env.user.employee_ids.name,
                        'sbu_project_budget_line_id': rec.project_expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                        'project_budget_id': self.sbu_project_budget_id.id
                    })

    def confirm_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Finance'
            if self.revised_amount_ids and self.for_revise_line:

                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                        [('sbu_project_budget_line_id', '=', rec.project_expense_id.id),
                         ('head_of_expense', '=', rec.project_expense_id.head_of_expense),
                         ('revise_budget_status', 'in', ['applied'])])
                    if log_data:
                        log_data.write({
                            'head_of_expense': rec.project_expense_id.head_of_expense,
                            'revised_amount': line_changes,
                            'total_amount': rec.project_expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'sbu_project_budget_line_id': rec.project_expense_id.id,
                            'state': 'Approved By L2',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_l2',
                            'project_budget_id': self.sbu_project_budget_id.id
                        })

    def Cancel_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Cancel'

    def confirm_finance(self):
        if self.pending_at == 'Finance':
            for lines in self.sbu_project_budget_line_ids:
                if not lines.account_code_id:
                    raise ValidationError(f'Account Code is  not set for the expense {lines.head_of_expense}')
            self.pending_at = 'cfo'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                        [('sbu_project_budget_line_id', '=', rec.project_expense_id.id),
                         ('head_of_expense', '=', rec.project_expense_id.head_of_expense),
                         ('revise_budget_status', 'in', ['applied', 'approved_by_l2', 'approved_by_finance'])])
                    if log_data:
                        log_data.write({
                            'head_of_expense': rec.project_expense_id.head_of_expense,
                            'revised_amount': line_changes,
                            'total_amount': rec.project_expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'sbu_project_budget_line_id': rec.project_expense_id.id,
                            'state': 'Approved By Finance',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_finance',
                        })

    def Cancel_finance(self):
        if self.pending_at == 'Finance':
            self.pending_at = 'Cancel'

    def confirm_cfo(self):
        if self.pending_at == 'cfo':
            # for lines in self.sbu_project_budget_line_ids:
            #     if not lines.account_code_id:
            #         raise ValidationError(f'Account Code is  not set for the expense {lines.head_of_expense}')
            self.pending_at = 'Approver'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                        [('sbu_project_budget_line_id', '=', rec.project_expense_id.id),
                         ('head_of_expense', '=', rec.project_expense_id.head_of_expense),
                         ('revise_budget_status', 'in',
                          ['applied', 'approved_by_l2', 'approved_by_finance', 'approved_by_cfo'])])
                    if log_data:
                        log_data.write({
                            'head_of_expense': rec.project_expense_id.head_of_expense,
                            'revised_amount': line_changes,
                            'total_amount': rec.project_expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'sbu_project_budget_line_id': rec.project_expense_id.id,
                            'state': 'Approved By CFO',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_cfo',
                        })

    def Cancel_cfo(self):
        if self.pending_at == 'cfo':
            self.pending_at = 'Cancel'

    def confirm_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'Validate'
            if self.sbu_project_budget_line_ids and self.for_new_line:
                for line in self.sbu_project_budget_line_ids:
                    line.sbu_project_budget_id = self.sbu_project_budget_id
                    line.state = 'validate'
                    line.id_new_line_bool = True
            if self.revised_amount_ids and self.for_revise_line:

                for data in self.revised_amount_ids:

                    line_changes = self.format_revised_amounts(data)
                    log_data = self.env['kw_revise_sbu_project_budget_action_log'].sudo().search(
                        [('sbu_project_budget_line_id', '=', data.project_expense_id.id),
                         ('head_of_expense', '=', data.project_expense_id.head_of_expense),
                         ('revise_budget_status', 'in', ['applied', 'L2 Approved', 'approved_by_finance'])])
                    if log_data:
                        log_data.write({
                            'head_of_expense': data.project_expense_id.head_of_expense,
                            'revised_amount': line_changes,
                            'total_amount': data.project_expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'sbu_project_budget_line_id': data.project_expense_id.id,
                            'state': 'Approved By Finance',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_approver',
                        })

                    if data.apr_budget:
                        data.project_expense_id.apr_budget = data.project_expense_id.apr_budget + data.apr_budget
                    if data.may_budget:
                        data.project_expense_id.may_budget = data.project_expense_id.may_budget + data.may_budget
                    if data.jun_budget:
                        data.project_expense_id.jun_budget = data.project_expense_id.jun_budget + data.jun_budget
                    if data.jul_budget:
                        data.project_expense_id.jul_budget = data.project_expense_id.jul_budget + data.jul_budget
                    if data.aug_budget:
                        data.project_expense_id.aug_budget = data.project_expense_id.aug_budget + data.aug_budget
                    if data.sep_budget:
                        data.project_expense_id.sep_budget = data.project_expense_id.sep_budget + data.sep_budget
                    if data.oct_budget:
                        data.project_expense_id.oct_budget = data.project_expense_id.oct_budget + data.oct_budget
                    if data.nov_budget:
                        data.project_expense_id.nov_budget = data.project_expense_id.nov_budget + data.nov_budget
                    if data.dec_budget:
                        data.project_expense_id.dec_budget = data.project_expense_id.dec_budget + data.dec_budget
                    if data.jan_budget:
                        data.project_expense_id.jan_budget = data.project_expense_id.jan_budget + data.jan_budget
                    if data.feb_budget:
                        data.project_expense_id.feb_budget = data.project_expense_id.feb_budget + data.feb_budget
                    if data.mar_budget:
                        data.project_expense_id.mar_budget = data.project_expense_id.mar_budget + data.mar_budget
                    data.project_expense_id.state = 'validate'
                    data.project_expense_id.id_revise_bool = True

                    data.project_expense_id.calulate_total_planed_amount()

    def cancel_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'Cancel'

    def revert_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'L1'

    def revert_finance(self):
        if self.pending_at == 'Finance':
            self.pending_at = 'L2'

    def revert_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'cfo'

    def revert_cfo(self):
        if self.pending_at == 'cfo':
            self.pending_at = 'Finance'


class RevisedAmount(models.Model):
    _name = 'revised_sbu_project_budget_data'
    _description = 'Revised project Budget'

    month_revies = fields.Selection(string="Month of Revies",
                                    selection=[('April', 'Apr'), ('May', 'May'), ('Jun', 'Jun'),
                                               ('July', 'July'), ('August', 'Aug'),
                                               ('September', 'Sep'), ('October', 'Oct'),
                                               ('November', 'Nov'), ('December', 'Dec'), ('January', 'Jan'),
                                               ('February', 'Feb'), ('March', 'Mar')])
    revised_amount = fields.Float(string='Revise Amount')
    wizard_id = fields.Many2one('revised_sbu_project_budget_wizard', string='Wizard')

    project_expense_id = fields.Many2one('kw_sbu_project_budget_line')
    head_of_expense = fields.Char('Particular')
    account_code_id = fields.Many2one('account.account', 'Account code')
    work_order_type = fields.Selection([
        ('work_order', 'Work Order'),
        ('opportunity', 'Opportunity'),
    ], default='work_order', string='Order Type', track_visibility='always')
    opportunity_name = fields.Char(string='Opportunity Name')
    order_code = fields.Char('Order Code', related='order_id.crm_id.code', store=True)
    project_code = fields.Char('Work Order Code', related='project_id.wo_code', store=True)
    client = fields.Char(string='Client Name')
    order_id = fields.Many2one('project.project', 'Order Name')
    project_id = fields.Many2one('kw_project_budget_master_data', 'Project Name')
    order_value = fields.Char(string='Order Value')
    category_id = fields.Many2one('kw_sbu_project_category_master', string='Category')
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount')
    head_expense_type = fields.Selection(string='Expenses/Income',
                                         selection=[('Income', 'Income'), ('Expenses', 'Expenses')])
    # actual_amount = fields.Float('Expenses Amount', compute="_compute_practical_amount", readonly=True)
    billing_amount = fields.Float('Billing Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('cancel', 'Cancelled'),
        ('re_apply', 'Reapply'),
        ('re_f_approved', 'ReApproved')
    ], 'Status', default='draft', required=True, readonly=True, copy=False, track_visibility='always')
    currency_id = fields.Many2one('res.currency')

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                  'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget',
                  'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget')
    def calulate_total_planed_amount(self):
        if not self._context.get('non_treasury_budget'):
            # for rec in self:
            self.total_amount = False
            self.total_amount = self.apr_budget + self.may_budget + self.jun_budget + \
                                self.jul_budget + self.aug_budget + self.sep_budget + \
                                self.oct_budget + self.nov_budget + self.dec_budget + \
                                self.jan_budget + self.feb_budget + self.mar_budget


class SbuProjectBudgetLinewizard(models.Model):
    _name = 'kw_sbu_project_line_wizard'
    _rec_name = 'project_expense_id'

    wizard_id = fields.Many2one('revised_sbu_project_budget_wizard', string='Wizard')
    project_expense_id = fields.Many2one('kw_sbu_project_budget_line')
    head_of_expense = fields.Char('Particular')
    account_code_id = fields.Many2one('account.account', 'Account code')
    work_order_type = fields.Selection([
        ('work_order', 'Work Order'),
        ('opportunity', 'Opportunity'),
    ], default='work_order', string='Order Type', track_visibility='always')
    opportunity_name = fields.Char(string='Opportunity Name')
    order_code = fields.Char('Order Code', related='order_id.crm_id.code', store=True)
    project_code = fields.Char('Work Order Code', related='project_id.wo_code', store=True)
    client = fields.Char(string='Client Name')
    order_id = fields.Many2one('project.project', 'Order Name')
    project_id = fields.Many2one('kw_project_budget_master_data', 'Project Name')
    order_value = fields.Char(string='Order Value')
    category_id = fields.Many2one('kw_sbu_project_category_master', string='Category')
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount')
    head_expense_type = fields.Selection(string='Expenses/Income',
                                         selection=[('Income', 'Income'), ('Expenses', 'Expenses')])
    # actual_amount = fields.Float('Expenses Amount', compute="_compute_practical_amount", readonly=True)
    billing_amount = fields.Float('Billing Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('cancel', 'Cancelled'),
        ('re_apply', 'Reapply'),
        ('re_f_approved', 'ReApproved')
    ], 'Status', default='draft', readonly=True, copy=False, track_visibility='always')
    currency_id = fields.Many2one('res.currency')


class kw_crm_lead_inherit(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record.ensure_one()
            if record.code:
                if self._context.get('by_crm_code'):
                    record_name = str(record.code)
                else:
                    record_name = str(record.code) + ' | ' + str(record.name)
            else:
                record_name = str(record.name)
            result.append((record.id, record_name))
        return result


class splltProjectwizard(models.TransientModel):
    _name = "split_project_budget_wizard"

    def _get_budget_line_data(self):
        rec = self.env['kw_sbu_project_budget_line'].browse(self.env.context.get('active_ids'))
        return rec

    project_budget_id = fields.Many2one('kw_sbu_project_budget_line', 'Project Budget', default=_get_budget_line_data)
    budget_line_ids = fields.One2many('split_project_budget_wizard_line', 'wiz_id')
    head_of_expense = fields.Char('Name of expenses', related='project_budget_id.head_of_expense')
    work_order_type = fields.Selection(related='project_budget_id.work_order_type', string='Order Type', )
    opportunity_name = fields.Char(related='project_budget_id.opportunity_name', string='Opportunity Name')
    project_code = fields.Char(string='Work Order Code', related='project_budget_id.project_code')
    client = fields.Char(related='project_budget_id.client', string='Client Name')
    project_id = fields.Many2one(related='project_budget_id.project_id', string='Project Name')
    order_value = fields.Char(related='project_budget_id.order_value', string='Order Value')
    category_id = fields.Many2one(related='project_budget_id.category_id', string='Category')
    apr_budget = fields.Float(related='project_budget_id.apr_budget')
    may_budget = fields.Float(related='project_budget_id.may_budget')
    jun_budget = fields.Float(related='project_budget_id.jun_budget')
    jul_budget = fields.Float(related='project_budget_id.jul_budget')
    aug_budget = fields.Float(related='project_budget_id.aug_budget')
    sep_budget = fields.Float(related='project_budget_id.sep_budget')
    oct_budget = fields.Float(related='project_budget_id.oct_budget')
    nov_budget = fields.Float(related='project_budget_id.nov_budget')
    dec_budget = fields.Float(related='project_budget_id.dec_budget')
    jan_budget = fields.Float(related='project_budget_id.jan_budget')
    feb_budget = fields.Float(related='project_budget_id.feb_budget')
    mar_budget = fields.Float(related='project_budget_id.mar_budget')
    total_amount = fields.Float(related='project_budget_id.total_amount')
    account_code_id = fields.Many2one('account.account', 'Account code', related='project_budget_id.account_code_id')
    head_expense_type = fields.Selection(string='Head of Expenses', related='project_budget_id.head_expense_type')

    def split_project_budget(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_sbu_project_budget_line'].sudo().search([('id', '=', active_ids)])
        project_budget_line = self.env['kw_sbu_project_budget_line'].sudo().browse(active_ids)
        total_amount = project_budget_line.total_amount
        month_budget_sums = {
            'apr_budget': sum(self.budget_line_ids.mapped('apr_budget')),
            'may_budget': sum(self.budget_line_ids.mapped('may_budget')),
            'jun_budget': sum(self.budget_line_ids.mapped('jun_budget')),
            'jul_budget': sum(self.budget_line_ids.mapped('jul_budget')),
            'aug_budget': sum(self.budget_line_ids.mapped('aug_budget')),
            'sep_budget': sum(self.budget_line_ids.mapped('sep_budget')),
            'oct_budget': sum(self.budget_line_ids.mapped('oct_budget')),
            'nov_budget': sum(self.budget_line_ids.mapped('nov_budget')),
            'dec_budget': sum(self.budget_line_ids.mapped('dec_budget')),
            'jan_budget': sum(self.budget_line_ids.mapped('jan_budget')),
            'feb_budget': sum(self.budget_line_ids.mapped('feb_budget')),
            'mar_budget': sum(self.budget_line_ids.mapped('mar_budget'))
        }

        new_monthly_amounts = {
            'apr_budget': sum(self.budget_line_ids.mapped('apr_budget')),
            'may_budget': sum(self.budget_line_ids.mapped('may_budget')),
            'jun_budget': sum(self.budget_line_ids.mapped('jun_budget')),
            'jul_budget': sum(self.budget_line_ids.mapped('jul_budget')),
            'aug_budget': sum(self.budget_line_ids.mapped('aug_budget')),
            'sep_budget': sum(self.budget_line_ids.mapped('sep_budget')),
            'oct_budget': sum(self.budget_line_ids.mapped('oct_budget')),
            'nov_budget': sum(self.budget_line_ids.mapped('nov_budget')),
            'dec_budget': sum(self.budget_line_ids.mapped('dec_budget')),
            'jan_budget': sum(self.budget_line_ids.mapped('jan_budget')),
            'feb_budget': sum(self.budget_line_ids.mapped('feb_budget')),
            'mar_budget': sum(self.budget_line_ids.mapped('mar_budget'))
        }

        total_new_lines_amount = sum(self.budget_line_ids.mapped('total_amount'))
        if total_new_lines_amount > total_amount:
            raise ValidationError(
                "The sum of budgets for newly created lines does not match the total amount of the original budget amount.")

        for rec in self.budget_line_ids:
            new_value = ''
            if project_budget_line.sequence_ref and project_budget_line.sequence_ref.startswith('P'):
                # Extract the numeric part from the sequence_ref
                import re
                pattern = r'P(\d+)([A-Z]*)'
                match = re.match(pattern, project_budget_line.sequence_ref)
                if match:
                    numeric_part = match.group(1)
                    existing_suffix = match.group(2) or ''

                    # Search for existing sequences with the same numeric part
                    dataa = self.env['kw_sbu_project_budget_line'].sudo().search([
                        ('sbu_project_budget_id', '=', project_budget_line.sbu_project_budget_id.id),
                        ('sequence_ref', 'like', f'P{numeric_part}%')
                    ])
                    suffixes = []
                    for recc in dataa:
                        suffix_match = re.match(pattern, recc.sequence_ref)
                        if suffix_match:
                            suffixes.append(suffix_match.group(2))

                    # Determine the next suffix
                    if suffixes:
                        sorted_suffixes = sorted(suffixes)
                        last_suffix = sorted_suffixes[-1]
                        if last_suffix:
                            next_suffix = chr(ord(last_suffix[-1]) + 1)
                            new_value = f"P{numeric_part}{existing_suffix}{next_suffix}"
                        else:
                            new_value = f"P{numeric_part}A"
                    else:
                        new_value = f"P{numeric_part}A"
                else:
                    new_value = project_budget_line.sequence_ref

            new_budget_line = self.env['kw_sbu_project_budget_line'].sudo().create(
                {'head_of_expense': rec.head_of_expense,
                 'account_code_id': rec.account_code_id.id,
                 'work_order_type': rec.work_order_type,
                 'opportunity_name': rec.opportunity_name,
                 'project_code': rec.project_code,
                 'client': rec.client,
                 'project_id': rec.project_id.id,
                 'order_value': rec.order_value,
                 'category_id': rec.category_id.id,
                 'apr_budget': rec.apr_budget,
                 'may_budget': rec.may_budget,
                 'jun_budget': rec.jun_budget,
                 'jul_budget': rec.jul_budget,
                 'aug_budget': rec.aug_budget,
                 'sep_budget': rec.sep_budget,
                 'oct_budget': rec.oct_budget,
                 'nov_budget': rec.nov_budget,
                 'dec_budget': rec.dec_budget,
                 'jan_budget': rec.jan_budget,
                 'feb_budget': rec.feb_budget,
                 'mar_budget': rec.mar_budget,
                 'total_amount': rec.total_amount,
                 'head_expense_type': rec.head_expense_type,
                 'sbu_project_budget_id': data.sbu_project_budget_id.id,
                 'state': 'validate',
                 'sequence_ref': new_value,
                 'hide_split_button_boolean': True,
                 'revised_button_hide_boolean': True
                 })

        data.write({
            month: project_budget_line[month] - new_monthly_amounts[month]
            for month in month_budget_sums
        })
        data.write({'total_amount': total_amount - sum(new_monthly_amounts.values())})


class SplitProjectWizardline(models.TransientModel):
    _name = 'split_project_budget_wizard_line'
    _description = 'Split Button Wizard'

    wiz_id = fields.Many2one('split_project_budget_wizard')
    head_of_expense = fields.Char('Name of expenses', required=True)
    account_code_id = fields.Many2one('account.account', 'Account code')
    work_order_type = fields.Selection([
        ('work_order', 'Work Order'),
        ('opportunity', 'Opportunity'),
    ], default='work_order', string='Order Type', track_visibility='always')
    opportunity_name = fields.Char(string='Opportunity Name')
    project_code = fields.Char('Work Order Code', related='project_id.wo_code', store=True)
    client = fields.Char(string='Client Name')
    project_id = fields.Many2one('kw_project_budget_master_data', 'Project Name')
    order_value = fields.Char(string='Order Value')
    category_id = fields.Many2one('kw_sbu_project_category_master', string='Category', required=True)
    apr_budget = fields.Float('Apr')
    may_budget = fields.Float('May')
    jun_budget = fields.Float('Jun')
    jul_budget = fields.Float('Jul')
    aug_budget = fields.Float('Aug')
    sep_budget = fields.Float('Sep')
    oct_budget = fields.Float('Oct')
    nov_budget = fields.Float('Nov')
    dec_budget = fields.Float('Dec')
    jan_budget = fields.Float('Jan')
    feb_budget = fields.Float('Feb')
    mar_budget = fields.Float('Mar')
    total_amount = fields.Float('Total Amount')
    head_expense_type = fields.Selection(string='Head of Expenses',
                                         selection=[('Income', 'Income'), ('Expenses', 'Expenses')], required=True)

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                  'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget',
                  'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget')
    def calulate_total_planed_amount(self):
        self.total_amount = False
        self.total_amount = self.apr_budget + self.may_budget + self.jun_budget + \
                            self.jul_budget + self.aug_budget + self.sep_budget + \
                            self.oct_budget + self.nov_budget + self.dec_budget + \
                            self.jan_budget + self.feb_budget + self.mar_budget
