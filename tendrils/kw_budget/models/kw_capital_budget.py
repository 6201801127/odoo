# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import os
import tempfile
import xlsxwriter
import base64
import logging

_logger = logging.getLogger('****************Capital Budget Report****************')

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


class AccountingCapitalBudget(models.Model):
    _name = 'kw_capital_budget'
    _description = "Capital Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'fiscal_year_id'

    def _get_department_user(self):
        domain = [('id', '=', 0)]
        user = self.env.user.employee_ids
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        if user:
            domain = []
            budget_department_id = self.env['kw_budget_dept_mapping'].search([
                '|', ('level_2_approver_capital.id', '=', user.id),
                ('level_1_approver_capital.id', '=', user.id),
                ('state', '=', 'approve'),
                ('fiscal_year', '=', current_fiscal.id)])
            if budget_department_id:
                department_ids = [department.id for department in budget_department_id if
                                  department.capital_boolean == True]
                domain = [('id', 'in', department_ids)]
        return domain

    # name = fields.Char('Budget Name')
    department_id = fields.Many2one('hr.department', 'Department', readonly=True,
                                    default=lambda self: self.get_selfEmpdeptDetails())
    division_id = fields.Many2one('hr.department', 'Division', readonly=True,
                                  default=lambda self: self.get_selfEmpdivisionDetails())
    section_id = fields.Many2one('hr.department', 'Section', readonly=True,
                                 default=lambda self: self.get_selfEmpsectionDetails())
    branch_id = fields.Many2one('kw_res_branch', 'Branch', readonly=True,
                                default=lambda self: self.get_selfEmpbranchDetails())
    fiscal_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', compute='_compute_fiscal_year', store=True)
    budget_department = fields.Many2one('kw_budget_dept_mapping', 'Budget For', domain=_get_department_user,
                                        track_visibility='always')
    budget_dept = fields.Many2one('hr.department', 'Department', related='budget_department.department_id', store=True)
    budget_division = fields.Many2one('hr.department', 'Division', related='budget_department.division_id', store=True)
    budget_section = fields.Many2one('hr.department', 'Section', related='budget_department.section_id', store=True)
    pending_at_ids = fields.Many2many('hr.employee', string='Pending at')
    revise_budget_action_log_ids = fields.One2many('kw_revise_budget_action_log', 'capital_budget_id',
                                                   'Capital Budget Log')
    state = fields.Selection([
        ('draft', 'L1'),
        ('to_approve', 'L2'),
        ('approved', 'Finance'),
        ('cfo', 'Finance(CFO)'),
        ('confirm', 'Approval'),
        ('validate', 'Approved'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    capital_budget_line_ids = fields.One2many('kw_capital_budget_line', 'capital_budget_id', 'Capital Budget Lines')
    cb_pending_at = fields.Char(string="Pending At")
    approver_head_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    revised_boolean = fields.Boolean()
    revised_amount = fields.Float()
    date_from = fields.Date('Start Date', states={'to_approve': [('readonly', True)]})
    date_to = fields.Date('End Date', states={'to_approve': [('readonly', True)]})
    add_expense_line_hide_boolean = fields.Boolean()
    capital_revised_finance_approval_boolean = fields.Boolean()
    capital_revised_approver_approval_boolean = fields.Boolean()
    finance_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    generate_seq_boolean = fields.Boolean(string='Generate Sequence Boolean')
    take_action_view_bool = fields.Boolean('Boolean', compute='_get_bool_enable')
    revert_finance = fields.Boolean('Boolean', compute='_get_bool_enable_revert')
    revert_cfo = fields.Boolean('Boolean', compute='_get_bool_enable_revert')
    revert_approver = fields.Boolean('Boolean', compute='_get_bool_enable_revert')
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

    def _get_bool_enable_revert(self):
        for rec in self:
            rec.revert_finance = True if rec.state == 'approved' and self.user_has_groups(
                'kw_budget.group_finance_kw_budget') else False
            rec.revert_cfo = True if rec.state == 'cfo' and self.user_has_groups(
                'kw_budget.group_cfo_kw_budget') else False
            rec.revert_approver = True if rec.state == 'confirm' and self.user_has_groups(
                'kw_budget.group_approver_kw_budget') else False

    @api.multi
    @api.depends('date_from', 'date_to')
    def _compute_fiscal_year(self):
        for record in self:
            fiscal_year = self.env['account.fiscalyear'].search([
                ('date_start', '<=', record.date_from),
                ('date_stop', '>=', record.date_to)
            ])
            record.fiscal_year_id = fiscal_year.id

    @api.constrains('date_from', 'date_to')
    def date_validate(self):
        for budget in self:
            if budget.date_to < budget.date_from:
                raise ValidationError('Month start date cant be less than end date.')

    @api.constrains('fiscal_year_id', 'capital_budget_line_ids')
    def _validate_budget_details(self):
        for budget in self:
            if budget.fiscal_year_id and not budget.capital_budget_line_ids:
                raise ValidationError('Please add Budget details.')

    # @api.constrains('fiscal_year_id', 'budget_department')
    # def _check_duplicate_revenue_budget(self):
    #     for record in self:
    #         existing_record = self.search([
    #             ('fiscal_year_id', '=', record.fiscal_year_id.id),
    #             ('budget_department', '=', record.budget_department.id),
    #             ('id', '!=', record.id),
    #             ('state', 'not in', ['cancel'])
    #         ])
    #         if existing_record:
    #             raise ValidationError("A record for this fiscal year already exists.")

    def get_boolean_all(self):
        for rec in self:
            rec.approver_head_boolean = True if rec.state == 'to_approve' and self.env.user.employee_ids.id in rec.budget_department.level_2_approver_capital.ids else False
            rec.finance_revert_back_boolean = True if rec.state == 'approved' and self.env.user.has_group(
                'kw_budget.group_finance_kw_budget') else False

    @api.multi
    def get_selfEmpdeptDetails(self):
        uid = self.env.user.id
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.department_id

    @api.multi
    def get_selfEmpdivisionDetails(self):
        uid = self.env.user.id
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.division

    @api.multi
    def get_selfEmpsectionDetails(self):
        uid = self.env.user.id
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.practise

    @api.multi
    def get_selfEmpbranchDetails(self):
        uid = self.env.user.id
        emp_details = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        return emp_details.base_branch_id

    def apply_budget(self):
        for rec in self:
            if self.env.user.employee_ids.id in rec.budget_department.level_2_approver_capital.ids:
                finance_group = self.env.ref(
                    'kw_budget.group_finance_kw_budget')
                finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                if not finance_users:
                    raise ValidationError("No users found in the finance group.")
                approver_ids = finance_users.mapped('employee_ids.id')
                rec.write({'state': 'approved',
                           'pending_at_ids': [(6, 0, approver_ids)]})
                for recc in rec.capital_budget_line_ids:
                    recc.state = 'to_approve'
            else:
                approver_ids = rec.budget_department.level_2_approver_capital.ids
                rec.write({'state': 'to_approve',
                           'pending_at_ids': [(6, 0, approver_ids)]})
                for recc in rec.capital_budget_line_ids:
                    recc.state = 'to_approve'

    def action_budget_confirm(self):
        finance_group = self.env.ref(
            'kw_budget.group_finance_kw_budget')
        finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
        if not finance_users:
            raise ValidationError("No users found in the finance group.")
        approver_ids = finance_users.mapped('employee_ids.id')
        for rec in self:
            rec.write({'state': 'approved',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.capital_budget_line_ids:
                recc.state = 'to_approve'

    def action_budget_validate(self):
        approver_group = self.env.ref(
            'kw_budget.group_cfo_kw_budget')
        approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if not approver_users:
            raise ValidationError("No users found in the Finance(CFO) group.")
        approver_ids = approver_users.mapped('employee_ids.id')
        for rec in self:
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                for recc in rec.capital_budget_line_ids:
                    if not recc.account_code_id:
                        raise ValidationError(f'Account Code is  not set for the expense {recc.name_of_expenses}')
                    recc.state = 'confirm'
            rec.write({'state': 'cfo',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            # for data in rec.capital_budget_line_ids:
            #     data.state = 'confirm'

    def action_budget_revert_back(self):
        for rec in self:
            rec.write({'state': 'draft',
                       'add_expense_line_hide_boolean': False,
                       'pending_at_ids': [(6, 0, [])]})
            for recc in rec.capital_budget_line_ids:
                recc.state = 'draft'
                recc.revised_button_hide_boolean = False

    def action_budget_validate_cfo(self):
        approver_group = self.env.ref(
            'kw_budget.group_approver_kw_budget')
        approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if not approver_users:
            raise ValidationError("No users found in the approver group.")
        approver_ids = approver_users.mapped('employee_ids.id')
        for rec in self:
            #     if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            #         for recc in rec.capital_budget_line_ids:
            #             if not recc.account_code_id:
            #                 raise ValidationError(f'Account Code is  not set for the expense {recc.name_of_expenses}')
            #             recc.state = 'confirm'
            rec.write({'state': 'confirm',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            # for data in rec.capital_budget_line_ids:
            #     data.state = 'confirm'

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_budget_done(self):
        for rec in self:
            rec.write({'state': 'validate',
                       'add_expense_line_hide_boolean': True,
                       'pending_at_ids': [(6, 0, [])]})
            for recc in rec.capital_budget_line_ids:
                recc.revised_button_hide_boolean = True
                recc.state = 'validate'

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user.employee_ids
        l2_ids = []
        l1_ids = []
        if self._context.get('take_action_capital_budget'):
            l1_budget_obj = []
            l2_budget_obj = []
            budget_department_id = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_2_approver_capital.id', '=', user.id)])
            if budget_department_id:
                if len(budget_department_id) == 1:
                    query = "select id from kw_capital_budget where state = 'to_approve' and budget_department = " + str(
                        budget_department_id.id)
                if len(budget_department_id) > 1:
                    query = "select id from kw_capital_budget where state = 'to_approve' and  budget_department in " + str(
                        tuple(budget_department_id.ids))
                self._cr.execute(query)
                ids = self._cr.fetchall()
                if ids:
                    l2_ids = [x[0] for x in ids]
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver_capital.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_capital_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_capital_budget where budget_department in " + str(
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
                        FROM kw_capital_budget
                        WHERE state = 'confirm'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_capital_budget
                                WHERE state = 'cfo'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    cfo_budget_obj = [data[0] for data in lines_obj]

                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_capital_budget
                                WHERE state = 'approved'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + cfo_budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                finance_budget_obj = []
                query = """
                        SELECT id
                        FROM kw_capital_budget
                        WHERE state = 'cfo'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_capital_budget
                                WHERE state = 'approved'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                        SELECT id
                        FROM kw_capital_budget
                        WHERE state = 'approved'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                budget_obj = budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)
            elif self.env.user.has_group('kw_budget.group_l2_kw_budget'):

                budget_obj = l2_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)
            else:
                budget_obj = l1_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('take_action_view_bool'):
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver_capital.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_capital_budget where state = 'validate' and  budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_capital_budget where state = 'validate' and budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('capital_budget_create'):
            l1_ids = []
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver_capital.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_capital_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_capital_budget where budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('view_status_capital_budget'):
            if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += ['|', ('create_uid', '=', self.env.user.id), '&',
                         ('budget_department.level_2_approver_capital', 'in', self.env.user.employee_ids.ids),
                         ('state', 'not in', ['draft'])]
            elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_approver_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_manager_kw_budget'):
                args += [('state', 'not in', ['draft'])]
            return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)

        return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)

    @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('take_action_capital_budget'):
    #         if self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', '&', ('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|', ('state', 'in', ['approved', 'confirm']), ('capital_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #             args += ['|', '&', ('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|', ('state', 'in', ['confirm']), ('capital_revised_approver_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_cfo_kw_budget'):
    #             args += ['|', ('state', 'in', ['to_approve', 'cfo']),
    #                      ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget') and self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', '|', ('state', 'in', ['confirm']), ('capital_revised_approver_approval_boolean', '=', True), '|', ('state', 'in', ['approved', 'confirm']), ('capital_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             args += [('state', 'in', ['to_approve']), ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #             args += ['|', ('state', 'in', ['cfo']), ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', ('state', 'in', ['approved', 'confirm']), ('capital_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #             args += ['|', ('state', 'in', ['confirm']), ('capital_revised_approver_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_manager_kw_budget'):
    #             return []
    #     elif self._context.get('view_status_capital_budget'):
    #         if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             args += ['|', ('create_uid', '=', self.env.user.id), '&', ('budget_department.level_2_approver_capital', 'in', self.env.user.employee_ids.ids), ('state', 'not in', ['draft'])]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group('kw_budget.group_approver_kw_budget') or self.env.user.has_group('kw_budget.group_manager_kw_budget'):
    #             args += [('state', 'not in', ['draft'])]
    #
    #     return super(AccountingCapitalBudget, self)._search(args, offset=offset, limit=limit, order=order, count=count,
    #                                                         access_rights_uid=access_rights_uid)

    def get_new_line_view(self):
        view_id = self.env.ref("kw_budget.kw_capital_budget_form_new_line").id
        action = {
            'name': 'Add Budget Expense',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_capital_budget',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {}
        }
        return action

    def open_capital_revise_wizard(self):
        return {
            'name': 'Revised Capital Budget Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'revised_budget_wizard',
            'view_id': self.env.ref('kw_budget.revised_amount_wizard_form').id,
            'target': 'new',
            'context': {
                'default_capital_budget_id': self.id,
                'kw_capital_wizard': True
            },
        }

    def capital_revised_add_line_submit(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_capital_budget'].sudo().search([('id', '=', active_ids)])
        for rec in self.capital_budget_line_ids:
            rec.capital_budget_id = active_ids
            rec.state = 'to_approve'
            rec.edit_button_hide_boolean = True
            data.capital_revised_finance_approval_boolean = True
            rec.finance_approved_button_boolean = True
            rec.revised_button_hide_boolean = False
            data.add_expense_line_hide_boolean = False
        self.unlink()

    def action_capital_budget_generate_id(self):
        # if not self.generate_seq_boolean:

        params = self.env['ir.config_parameter'].sudo()
        count = params.get_param('id_count_capital')

        line_data = self.env['kw_capital_budget_line'].sudo().search(
            [('state', '=', 'validate'), ('capital_budget_id.fiscal_year_id', '=', self.fiscal_year_id.id)])
        sequence_map = {}
        for rec in line_data:
            department_name = rec.capital_budget_id.budget_department.name
            if department_name not in sequence_map:
                sequence_map[department_name] = []
            sequence_map[department_name].append(rec)
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
                    # elif rec.id_new_line_bool:
                    #     sequence_number_copy = rec.sequence_ref
                    #     if 'A' not in rec.sequence_ref:
                    #         sequence_number_copy = 'A' + str(rec.sequence_ref)

                if not rec.sequence_ref:
                    sequence_number_copy = sequence_number
                    if rec.id_new_line_bool:
                        sequence_number_copy = 'A' + str(sequence_number_copy)
                        if rec.id_revise_bool:
                            sequence_number_copy = 'R' + str(sequence_number_copy)
                        params.set_param('id_count_capital', sequence_number)
                        sequence_number += 1

                    elif rec.id_revise_bool:
                        sequence_number_copy = 'R' + str(sequence_number_copy)

                        params.set_param('id_count_capital', sequence_number)
                        sequence_number += 1
                    else:
                        sequence_number_copy = sequence_number_copy
                        params.set_param('id_count_capital', sequence_number)
                        sequence_number += 1
                rec.sequence_ref = sequence_number_copy

    def print_capital_report(self):
        '''
        this function is used to print the XLXS report
        '''

        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'Capital Budget.xlsx')
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format({'num_format': 'd-m-yyyy',
                                           'align': 'center',
                                           'font_color': 'white',
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
            'align': 'left'})
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
        date_format.set_bg_color('#108fbb')
        date_format.set_font_name('Agency FB')
        date_format.set_border(style=2)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('#108fbb')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet('Capital Budget Report')
        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 8)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 30)
        worksheet.set_column(4, 4, 30)
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
        worksheet.set_row(1, 100)
        row, col = 0, 0
        worksheet.merge_range(row, col, row, col + 21, "Capital Budget Report", style_header)
        row += 1
        worksheet.write(row, col, 'sr.No ', style_header2)
        worksheet.write(row, col + 1, 'ID', style_header2)
        worksheet.write(row, col + 2, 'Narration', style_header2)
        worksheet.write(row, col + 3, 'Month Start', style_header2)
        worksheet.write(row, col + 4, 'Month End', style_header2)
        worksheet.write(row, col + 5, 'Quantity', style_header2)
        worksheet.write(row, col + 6, 'Rate Per QTY', style_header2)
        worksheet.write(row, col + 7, 'Total', style_header2)
        worksheet.write(row, col + 8, 'April', style_header2)
        worksheet.write(row, col + 9, 'May', style_header2)
        worksheet.write(row, col + 10, 'June', style_header2)
        worksheet.write(row, col + 11, 'July', style_header2)
        worksheet.write(row, col + 12, 'August', style_header2)
        worksheet.write(row, col + 13, 'September', style_header2)
        worksheet.write(row, col + 14, 'October ', style_header2)
        worksheet.write(row, col + 15, 'November ', style_header2)
        worksheet.write(row, col + 16, 'December ', style_header2)
        worksheet.write(row, col + 17, 'January ', style_header2)
        worksheet.write(row, col + 18, 'Feburary ', style_header2)
        worksheet.write(row, col + 19, 'March ', style_header2)
        worksheet.write(row, col + 20, 'Next Fy Year', style_header2)
        worksheet.write(row, col + 21, 'Remarks', style_header2)
        if self:
            seq = 1
            apr, may, june, july, aug, sep, oct, nov, dec, jan, feb, mar, total = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            for lines in self.capital_budget_line_ids:
                row += 1

                date_from = lines.date_from
                date_from = date_from.strftime('%d-%m-%Y')
                date_to = lines.date_to
                date_to = date_to.strftime('%d-%m-%Y')
                worksheet.write(row, col, row, style_data)
                worksheet.write(row, col + 1, lines.sequence_ref, style_data)
                worksheet.write(row, col + 2, lines.name_of_expenses or '', style_data)
                worksheet.write(row, col + 3, date_from, style_data)
                worksheet.write(row, col + 4, date_to, style_data)
                worksheet.write(row, col + 5, lines.quantity, style_data)
                worksheet.write(row, col + 6, lines.rate_per_quantity, style_data)
                worksheet.write(row, col + 7, lines.total_amount, style_data2)
                worksheet.write(row, col + 8, lines.apr_budget, style_data)
                worksheet.write(row, col + 9, lines.may_budget, style_data)
                worksheet.write(row, col + 10, lines.jun_budget, style_data)
                worksheet.write(row, col + 11, lines.jul_budget or '', style_data)
                worksheet.write(row, col + 12, lines.aug_budget or '', style_data)
                worksheet.write(row, col + 13, lines.sep_budget, style_data)
                worksheet.write(row, col + 14, lines.oct_budget, style_data)
                worksheet.write(row, col + 15, lines.nov_budget, style_data)
                worksheet.write(row, col + 16, lines.dec_budget, style_data)
                worksheet.write(row, col + 17, lines.jan_budget, style_data)
                worksheet.write(row, col + 18, lines.feb_budget, style_data)
                worksheet.write(row, col + 19, lines.mar_budget, style_data)
                worksheet.write(row, col + 20, lines.next_fy_year, style_data)
                worksheet.write(row, col + 21, lines.remark, style_data)
                seq += 1

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
            worksheet.write(row, col + 7, total, style_data3)
            worksheet.write(row, col + 8, apr, style_data3)
            worksheet.write(row, col + 9, may, style_data3)
            worksheet.write(row, col + 10, june, style_data3)
            worksheet.write(row, col + 11, july or '', style_data3)
            worksheet.write(row, col + 12, aug or '', style_data3)
            worksheet.write(row, col + 13, sep, style_data3)
            worksheet.write(row, col + 14, oct, style_data3)
            worksheet.write(row, col + 15, nov, style_data3)
            worksheet.write(row, col + 16, dec, style_data3)
            worksheet.write(row, col + 17, jan, style_data3)
            worksheet.write(row, col + 18, feb, style_data3)
            worksheet.write(row, col + 19, mar, style_data3)

        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "Capital Budget.xlsx"
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


class CapitalBudgetLine(models.Model):
    _name = 'kw_capital_budget_line'
    _rec_name = 'name_of_expenses'

    name_of_expenses = fields.Char('Narration', required=True)
    account_code_id = fields.Many2one('account.account', 'Account code')
    amount_required = fields.Float('Amount Required')
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount', )
    # actual_amount = fields.Float(compute='_compute_practical_amount', readonly=True)
    date_from = fields.Date('Month Start', required=True)
    date_to = fields.Date('Month End', required=True)
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
    next_fy_year = fields.Float('Next FY Year')
    remark = fields.Text('Remark')
    capital_budget_id = fields.Many2one('kw_capital_budget', 'Capital Budget')
    # revised_button_boolean = fields.Boolean(compute='revised_button', store=False)
    revised_attempt_button_visible = fields.Boolean()
    expense_type = fields.Selection(string='Expenses Type',
                                    selection=[('Workorder', 'Workorder'), ('Treasury', 'Treasury')])
    revise_budget_action_log_ids = fields.One2many('kw_revise_budget_action_log', 'capital_budget_line_id',
                                                   'Capital Budget Log')
    quantity = fields.Integer('Quantity')
    rate_per_quantity = fields.Float('Rate per Quantity')
    approved_button_boolean = fields.Boolean()
    revised_button_hide_boolean = fields.Boolean()
    # revised_invisible_button = fields.Boolean(compute='get_button_revised', store=False)
    budgetary_position_id = fields.Many2one('account.budget.post')
    finance_approved_button_boolean = fields.Boolean()
    approver_approved_button_boolean = fields.Boolean()
    approver_reverted_button_boolean = fields.Boolean()
    edit_button_hide_boolean = fields.Boolean()
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
    sequence_ref = fields.Char(string='ID')
    hide_split_button_boolean = fields.Boolean(default=False)
    capital_budget_revise = fields.Many2one('revised_budget_wizard', string='Capital Budget suppor id')
    id_revise_bool = fields.Boolean(default=False)
    id_new_line_bool = fields.Boolean(default=False)

    @api.constrains('apr_budget', 'may_budget', 'jun_budget', 'jul_budget', 'aug_budget', 'sep_budget', 'oct_budget',
                    'nov_budget', 'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget', 'total_amount')
    def _check_total_amount(self):
        for record in self:
            total_budget = record.apr_budget + record.may_budget + record.jun_budget + record.jul_budget + record.aug_budget + record.sep_budget + record.oct_budget + record.nov_budget + record.dec_budget + record.jan_budget + record.feb_budget + record.mar_budget
            if total_budget != record.total_amount:
                raise ValidationError("Total monthly budgets must be equal to Total Amount.")

    @api.constrains('date_from', 'date_to')
    def date_validate(self):
        for budget in self:
            if budget.date_to < budget.date_from:
                raise ValidationError('Month start date cant be less than end date.')

    # @api.multi
    # def _compute_practical_amount(self):
    #     for line in self:
    #         acc_ids = line.budgetary_position_id.account_ids.ids
    #         date_to = line.date_to
    #         date_from = line.date_from
    #         aml_obj = self.env['account.move.line']
    #         domain = [('account_id', '=',
    #                    line.account_code_id.id),
    #                   ('date', '>=', date_from),
    #                   ('date', '<=', date_to)
    #                   ]   #('department_id', '=', line.capital_budget_id.budget_department.department_id.id)
    #         where_query = aml_obj._where_calc(domain)
    #         aml_obj._apply_ir_rules(where_query, 'read')
    #         from_clause, where_clause, where_clause_params = where_query.get_sql()
    #         select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

    #         self.env.cr.execute(select, where_clause_params)
    #         line.actual_amount = self.env.cr.fetchone()[0] or 0.0

    # def action_open_budget_entries(self):
    #     action = self.env['ir.actions.act_window'].for_xml_id('account', 'action_account_moves_all_a')
    #     action['domain'] = [('account_id', '=',
    #                          self.account_code_id.id),
    #                         ('date', '>=', self.date_from),
    #                         # ('date', '<=', self.date_to), ('department_id', '=', self.capital_budget_id.budget_department.department_id.id)
    #                         ]
    #     return action

    @api.onchange('amount_required', 'quantity', 'rate_per_quantity')
    def get_total_value(self):
        for rec in self:
            rec.total_amount = False
            rec.total_amount = rec.amount_required + rec.quantity * rec.rate_per_quantity

    def approve_revised_budget(self):
        for rec in self:
            log_data = self.env['kw_revise_budget_action_log'].search(
                [('capital_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.capital_budget_id.pending_at_ids = False
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.state = 're_f_approved'
                    rec.capital_budget_id.capital_revised_approver_approval_boolean = True  # record for search view
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_apply', 'to_approve']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_finance_approval_boolean = False  # record for search view
                        # rec.capital_budget_id.capital_revised_approver_approval_boolean = True  # record for search view
                        approver_group = self.env.ref(
                            'kw_budget.group_approver_kw_budget')
                        approver_group_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
                        if not approver_group_users:
                            raise ValidationError("No users found in the approver group.")
                        approver_ids = approver_group_users.mapped('employee_ids.id')
                        rec.capital_budget_id.pending_at_ids = [(6, False, approver_ids)]

                    log_data.write({
                        'revise_budget_status': 'approved_by_finance',
                        'approver_by': self.env.user.employee_ids.name,
                        'state': 'Finance Approved',
                        'total_amount': rec.total_amount,
                    })

                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.capital_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    data = self.env['revised_budget_wizard'].sudo().search([('expense_id', '=', rec.id)],
                                                                           limit=1)
                    rec.amount_required += data.revised_amount
                    rec.state = 'validate'
                    data.unlink()
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_approver_approval_boolean = False

                    log_data.write({
                        'revise_budget_status': 'approved_by_approver',
                        'approver_by': self.env.user.employee_ids.name,
                        'state': 'Approved',
                        'total_amount': rec.total_amount,
                    })

            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    if not rec.account_code_id:
                        raise ValidationError('Please set Account Code.')
                    rec.capital_budget_id.pending_at_ids = False
                    rec.state = 'confirm'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = True
                    rec.capital_budget_id.capital_revised_approver_approval_boolean = True  # for search method
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['to_approve', 're_apply']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_finance_approval_boolean = False  # for search method
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'validate'
                    rec.capital_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.capital_budget_id.add_expense_line_hide_boolean = True
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_approver_approval_boolean = False  # for search method

            # rec.capital_budget_id.pending_at_ids = False
            # rec.capital_budget_id.revised_boolean = False
            # rec.approved_button_boolean = False
            # rec.revised_button_hide_boolean = False
            # rec.amount_required += rec.capital_budget_id.revised_amount
            # rec.capital_budget_id.write(
            #     {'revise_budget_action_log_ids': [[0, 0, {'name_of_expenses': rec.name_of_expenses,
            #                                               'amount_required': rec.amount_required,
            #                                               'revised_amount': rec.capital_budget_id.revised_amount,
            #                                               'total_amount': rec.total_amount,
            #                                               'approver_by': self.env.user.employee_ids.name,
            #                                               'state': 'Approved',
            #                                               }]]})

    def reject_revised_budget(self):
        for rec in self:
            log_data = self.env['kw_revise_budget_action_log'].search(
                [('capital_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.state = 'validate'
                    rec.approver_approved_button_boolean = False
                    rec.finance_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.capital_budget_id.capital_revised_approver_approval_boolean = True  # record for search view
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_apply', 'to_approve']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_finance_approval_boolean = False  # record for search view
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'revise_budget_status': 'rejected_by_finance',
                    })
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.capital_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    data = self.env['revised_budget_wizard'].search([('expense_id', '=', rec.id)], limit=1)
                    rec.state = 'validate'
                    data.revised_amount_ids.unlink()
                    data.unlink()
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_approver_approval_boolean = False
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'total_amount': rec.total_amount,
                        'revise_budget_status': 'rejected_by_approver',
                    })
            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.capital_budget_id.pending_at_ids = False
                    rec.state = 'cancel'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_apply', 'to_approve']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_finance_approval_boolean = False  # for search method
                        rec.capital_budget_id.capital_revised_approver_approval_boolean = False  # for search method
                        rec.capital_budget_id.add_expense_line_hide_boolean = True
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'cancel'
                    rec.capital_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    val = []
                    for dataa in rec.capital_budget_id.capital_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.capital_budget_id.capital_revised_approver_approval_boolean = False  # for search method
                        rec.capital_budget_id.add_expense_line_hide_boolean = True

    def revised_data_send_back(self):
        for rec in self:
            log_data = self.env['kw_revise_budget_action_log'].search(
                [('capital_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.capital_budget_id.pending_at_ids = False
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = False
                    rec.edit_button_hide_boolean = True
                    log_data.write({
                        'state': 'Sent Back',
                        'approve_date': date.today(),
                    })

    def edit_budget_button(self):
        for rec in self:
            data = self.env['revised_budget_wizard'].sudo().search([('expense_id', '=', rec.id)], limit=1)
            default_revised_amount_ids = [
                {'month_revies': item.month_revies, 'revised_amount': item.revised_amount}
                for item in data.revised_amount_ids
            ]
            return {
                'name': 'Revised Capital Budget Wizard',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'revised_budget_wizard',
                'view_id': self.env.ref('kw_budget.revised_amount_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_name_of_expenses': rec.name_of_expenses,
                    # 'default_expense_type':rec.expense_type,
                    'default_date_from': rec.date_from,
                    'default_date_to': rec.date_to,
                    'default_expense_id': rec.id,
                    'default_revised_amount': data.revised_amount,
                    'default_remarks': data.remarks,
                    'default_revised_amount_ids': default_revised_amount_ids,
                },
            }


class RevisedBudgetWizard(models.Model):
    _name = 'revised_budget_wizard'
    _description = 'revised button wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'capital_budget_id'

    name_of_expenses = fields.Char(string='Narration', related='expense_id.name_of_expenses')
    # expense_type = fields.Selection(string='Expenses Type',selection=[('Workorder', 'Workorder'), ('Treasury', 'Treasury')], related='expense_id.expense_type')
    date_from = fields.Date('Month Start Date', related='expense_id.date_from')
    date_to = fields.Date('Month End Date', related='expense_id.date_to')
    revised_amount = fields.Float(string='Revise Amount')
    remarks = fields.Text(string='Remarks')
    expense_id = fields.Many2one('kw_capital_budget_line')
    revised_amount_ids = fields.One2many('revised_budget_data', 'wizard_id', string='Revised Amounts', store=True)
    capital_budget_id = fields.Many2one('kw_capital_budget', string="Capital Budget",
                                        default=lambda self: self.env['kw_capital_budget'].sudo().search(
                                            [('id', '=', self.env.context.get('active_id'))]))
    for_new_line = fields.Boolean('For New Budget Line')
    for_revise_line = fields.Boolean('For Revise Budget Line')
    capital_budget_line_ids = fields.One2many('kw_capital_budget_line', 'capital_budget_revise',
                                              string='Capital Budget Lines',
                                              copy=True)
    existing_capital_budget_line_ids = fields.One2many('kw_capital_budget_line_wizard', 'wizard_id',
                                                       'Capital Budget Lines')

    pending_at = fields.Selection(string="Status",
                                  selection=[('L1', ''), ('L2', 'L2'), ('Finance', 'Finance'), ('cfo', 'Finance(CFO)'),
                                             ('Approver', 'Approver'), ('Validate', 'Validate'),
                                             ('Cancel', 'Cancel')], default="L1", track_visibility='onchange')

    # existing_revenue_budget_line_ids = fields.One2many('kw_revenue_budget_line', 'revenue_budget_revise', 'Revenue Budget Lines')
    budget_department = fields.Char('Budget For')
    branch_id = fields.Char('Branch')

    show_apply = fields.Boolean('Show Apply', compute='get_boolean_all')
    pending_since = fields.Datetime('Pending Since', default=datetime.now(), compute='_get_pending_since')

    @api.depends('pending_at')
    def _get_pending_since(self):
        for rec in self:
            if rec.pending_at:
                rec.pending_since = datetime.now()
            else:
                rec.pending_since = ''

    def apply_l1(self):
        if self.pending_at == 'L1':
            self.pending_at = 'L2'

    def get_boolean_all(self):
        for rec in self:
            rec.show_apply = True if rec.pending_at == 'L1' and self.env.user.employee_ids.id in rec.capital_budget_id.budget_department.level_1_approver_capital.ids else False

    @api.onchange('capital_budget_id')
    def onchnage_capital_budget_details(self):
        if self.capital_budget_id:
            self.budget_department = self.capital_budget_id.budget_department.name
            self.branch_id = self.capital_budget_id.branch_id.name

    @api.onchange('revised_amount_ids')
    def _onchange_existing__capital_lines(self):
        if self.revised_amount_ids:
            new_lines = []
            self.existing_capital_budget_line_ids = [(5, 0, 0)]
            for rec in self.revised_amount_ids:
                if rec.expense_id:
                    rec.date_from = rec.expense_id.date_from
                    rec.date_to = rec.expense_id.date_to
                    rec.quantity = rec.expense_id.quantity
                    rec.rate_per_quantity = rec.expense_id.rate_per_quantity
                    rec.rate_per_quantity = rec.expense_id.rate_per_quantity
                    rec.total_amount = rec.expense_id.total_amount
                    rec.remark = rec.expense_id.remark
                    rec.next_fy_year = rec.expense_id.next_fy_year
                    new_lines.append((0, 0, {
                        "name_of_expenses": rec.expense_id.name_of_expenses,
                        "date_from": rec.expense_id.date_from,
                        "date_to": rec.expense_id.date_to,
                        "quantity": rec.expense_id.quantity,
                        "rate_per_quantity": rec.expense_id.rate_per_quantity,
                        "total_amount": rec.expense_id.total_amount,
                        "apr_budget": rec.expense_id.apr_budget,
                        "may_budget": rec.expense_id.may_budget,
                        "jun_budget": rec.expense_id.jun_budget,
                        "jul_budget": rec.expense_id.jul_budget,
                        "aug_budget": rec.expense_id.aug_budget,
                        "sep_budget": rec.expense_id.sep_budget,
                        "oct_budget": rec.expense_id.oct_budget,
                        "nov_budget": rec.expense_id.nov_budget,
                        "dec_budget": rec.expense_id.dec_budget,
                        "jan_budget": rec.expense_id.jan_budget,
                        "feb_budget": rec.expense_id.feb_budget,
                        "mar_budget": rec.expense_id.mar_budget,
                        "next_fy_year": rec.expense_id.next_fy_year,
                        "remark": rec.expense_id.remark,

                    }))
            self.existing_capital_budget_line_ids = new_lines

    def format_revised_amounts(self, line_obj):
        format_rev_amts_list = []
        format_rev_amts = ''
        for rec in line_obj:
            if rec.apr_budget:
                format_rev_amts += f"{'April'} : {str(rec.apr_budget)}"
            if rec.may_budget:
                format_rev_amts += f"{'May'} : {str(rec.may_budget)}"
            if rec.jun_budget:
                format_rev_amts += f"{'June'} : {str(rec.jun_budget)}"
            if rec.jul_budget:
                format_rev_amts += f"{'July'} : {str(rec.jul_budget)}"
            if rec.aug_budget:
                format_rev_amts += f"{'August'} : {str(rec.aug_budget)}"
            if rec.sep_budget:
                format_rev_amts += f"{'September'} : {str(rec.sep_budget)}"
            if rec.oct_budget:
                format_rev_amts += f"{'October'} : {str(rec.oct_budget)}"
            if rec.nov_budget:
                format_rev_amts += f"{'November'} : {str(rec.nov_budget)}"
            if rec.dec_budget:
                format_rev_amts += f"{'December'} : {str(rec.dec_budget)}"
            if rec.jan_budget:
                format_rev_amts += f"{'January'} : {str(rec.jan_budget)}"
            if rec.feb_budget:
                format_rev_amts += f"{'April'} : {str(rec.feb_budget)}"
            if rec.mar_budget:
                format_rev_amts += f"{'March'} : {str(rec.mar_budget)}"
            format_rev_amts_list.append(format_rev_amts)
        return ', '.join(format_rev_amts_list)

    def revised_amount_submit(self):
        data = self.env['revised_budget_wizard'].sudo().search(
            [('expense_id', '=', self.expense_id.id)]) - self
        data.unlink()
        for rec in self:
            rec.expense_id.capital_budget_id.capital_revised_finance_approval_boolean = True
            rec.expense_id.finance_approved_button_boolean = True
            rec.expense_id.revised_button_hide_boolean = False
            rec.expense_id.edit_button_hide_boolean = True
            rec.expense_id.state = 're_apply'
            rec.expense_id.capital_budget_id.revised_amount = self.revised_amount
            approver_group = self.env.ref(
                'kw_budget.group_finance_kw_budget')
            approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
            if not approver_users:
                raise ValidationError("No users found in the finance group.")
            approver_ids = approver_users.mapped('employee_ids.id')

            log_data = self.env['kw_revise_budget_action_log'].search(
                [('capital_budget_line_id', '=', rec.expense_id.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if log_data:
                log_data.write({
                    'revise_budget_status': 'applied',
                    'name_of_expenses': rec.expense_id.name_of_expenses,
                    'amount_required': rec.expense_id.amount_required,
                    'revised_amount': self.revised_amount,
                    'total_amount': rec.expense_id.total_amount,
                    'applied_by': self.env.user.employee_ids.name,
                    'capital_budget_line_id': rec.expense_id.id,
                    'state': 'Applied',
                })
            else:
                rec.expense_id.capital_budget_id.write({
                    'revise_budget_action_log_ids': [[0, 0, {
                        'revise_budget_status': 'applied',
                        'name_of_expenses': rec.expense_id.name_of_expenses,
                        'amount_required': rec.expense_id.amount_required,
                        'revised_amount': self.revised_amount,
                        'total_amount': rec.expense_id.total_amount,
                        'applied_by': self.env.user.employee_ids.name,
                        'capital_budget_line_id': rec.expense_id.id,
                        'state': 'Applied',
                    }]],
                    'pending_at_ids': [(6, 0, approver_ids)]
                })

    @api.multi
    def open_take_action_capital_budget_lines(self):
        ''' function is used to redirect revise/ADD revenue Budget lines list, form view. '''
        res = self.env.ref('kw_budget.action_revised_capital_budget_wizard').read()[0]
        res['context'] = {'create': False, 'edit': True}
        user = self.env.user.employee_ids
        budget_department_id = self.env['kw_budget_dept_mapping'].search([
            ('level_2_approver_capital.id', '=', user.id)])
        if budget_department_id:
            if len(budget_department_id) == 1:
                query = "select id from kw_capital_budget where budget_department = " + str(
                    budget_department_id.id)
            if len(budget_department_id) > 1:
                query = "select id from kw_capital_budget where budget_department in " + str(
                    tuple(budget_department_id.ids))
            self._cr.execute(query)
            ids = self._cr.fetchall()
            if ids:
                budget_obj = self.env['revised_budget_wizard'].search(
                    [('capital_budget_id', 'in', ids), ('pending_at', '=', 'L2')])
                res['views'] = [(self.env.ref('kw_budget.view_revised_amount_capital_wizard_tree').id, 'list'),
                                (self.env.ref('kw_budget.revised_amount_wizard_form').id, 'form')]
                res['domain'] = [('id', 'in', budget_obj.ids)]
                res['context'] = {'create': False, 'edit': True}

        if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            budget_obj = self.env['revised_budget_wizard'].search(
                [('pending_at', '=', 'Finance')])
            res['views'] = [(self.env.ref('kw_budget.view_revised_amount_capital_wizard_tree').id, 'list'),
                            (self.env.ref('kw_budget.revised_amount_wizard_form').id, 'form')]
            res['domain'] = [('id', 'in', budget_obj.ids)]
            res['context'] = {'create': False, 'edit': True}

        if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
            budget_obj = self.env['revised_budget_wizard'].search(
                [('pending_at', '=', 'Approver')])
            res['views'] = [(self.env.ref('kw_budget.view_revised_amount_capital_wizard_tree').id, 'list'),
                            (self.env.ref('kw_budget.revised_amount_wizard_form').id, 'form')]
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
        budget_department_id = self.env['kw_budget_dept_mapping'].sudo().search([
            ('level_2_approver_capital.id', '=', user.id)])
        if budget_department_id:
            if len(budget_department_id) == 1:
                query = "select id from kw_capital_budget where budget_department = " + str(
                    budget_department_id.id)
            if len(budget_department_id) > 1:
                query = "select id from kw_capital_budget where budget_department in " + str(
                    tuple(budget_department_id.ids))
            self._cr.execute(query)
            ids = self._cr.fetchall()
            if ids:
                l2_ids = [x[0] for x in ids]
                query = """
                            SELECT id
                            FROM revised_budget_wizard
                            WHERE capital_budget_id IN %s
                            AND pending_at = 'L2'
                        """
                self._cr.execute(query, (tuple(l2_ids),))
                lines_obj = self._cr.fetchall()
                l2_budget_obj = [data[0] for data in lines_obj]
        budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
            ('level_1_approver_capital.id', '=', user.id)])
        if budget_department_id_l1:
            if len(budget_department_id_l1) == 1:
                l1query = "select id from kw_capital_budget where budget_department = " + str(
                    budget_department_id_l1.id)
            if len(budget_department_id_l1) > 1:
                l1query = "select id from kw_capital_budget where budget_department in " + str(
                    tuple(budget_department_id_l1.ids))
            self._cr.execute(l1query)
            l1_ids = self._cr.fetchall()
            if l1_ids:
                l1_ids = [x[0] for x in l1_ids]
                query = """
                            SELECT id
                            FROM revised_budget_wizard
                            WHERE capital_budget_id IN %s
                        """
                self._cr.execute(query, (tuple(l1_ids),))
                lines_obj = self._cr.fetchall()
                l1_budget_obj = [data[0] for data in lines_obj]

        if self._context.get('take_action_view_status'):
            if self.env.user.has_group('kw_budget.group_manager_kw_budget'):
                query = """
                                        SELECT id
                                        FROM revised_budget_wizard
                                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                args = [('id', 'in', budget_obj)]
                return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
            finance_budget_obj = []
            cfo_budget_obj = []
            query = """
                        SELECT id
                        FROM revised_budget_wizard
                        WHERE pending_at = 'Approver'
                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            # print(budget_obj, 'approver')
            if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                query = """
                                SELECT id
                                FROM revised_budget_wizard
                                WHERE pending_at = 'cfo'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                cfo_budget_obj = [data[0] for data in lines_obj]

            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                                SELECT id
                                FROM revised_budget_wizard
                                WHERE pending_at = 'Finance'
                            """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                finance_budget_obj = [data[0] for data in lines_obj]

            budget_obj = budget_obj + cfo_budget_obj + finance_budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
            cfo_budget_obj = []
            budget_obj = []
            query = """
                            SELECT id
                            FROM revised_budget_wizard
                            WHERE pending_at = 'cfo'
                        """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            cfo_budget_obj = [data[0] for data in lines_obj]
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                            SELECT id
                            FROM revised_budget_wizard
                            WHERE pending_at = 'Finance'
                        """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'PPPPPPPPPPPPPPPPPPPPBB')
            budget_obj = cfo_budget_obj + budget_obj + l1_budget_obj + l2_budget_obj
            print(budget_obj, l1_budget_obj, l2_budget_obj, [('id', 'in', tuple(budget_obj))])
            args = [('id', 'in', budget_obj)]
            return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            query = """
                        SELECT id
                        FROM revised_budget_wizard
                        WHERE pending_at = 'Finance'
                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            # print(budget_obj, 'PPPPPPPPPPPPPPPPPPPPBB')
            budget_obj = budget_obj + l1_budget_obj + l2_budget_obj
            print(budget_obj, l1_budget_obj, l2_budget_obj, [('id', 'in', tuple(budget_obj))])
            args = [('id', 'in', budget_obj)]
            return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_l2_kw_budget'):
            domain_ids = []
            domain_ids = l2_budget_obj + l1_budget_obj
            # print(domain_ids, 'pppppfffffffffff')
            args = [('id', 'in', domain_ids)]

            return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)
        else:
            domain_ids = l1_budget_obj
            args = [('id', 'in', domain_ids)]
            return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)
        return super(RevisedBudgetWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                        count=count, access_rights_uid=access_rights_uid)

    def confirm_apply(self):
        # count = 0
        # if len(self.revised_amount_ids) > 0:
        #     count +=  len(self.revised_amount_ids)
        # if len(self.capital_budget_line_ids) > 0:
        #     count +=  len(self.capital_budget_line_ids)
        # if count == 0:
        #     raise ValidationError("Please add atleast one line.")
        self.onchnage_capital_budget_details()
        if self.pending_at == 'L1':
            self.pending_at = 'L2'
        if self.revised_amount_ids and self.for_revise_line:

            for rec in self.revised_amount_ids:
                line_changes = self.format_revised_amounts(rec)
                log_data = self.env['kw_revise_budget_action_log'].sudo().search(
                    [('capital_budget_line_id', '=', rec.expense_id.id),
                     ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                     ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
                if log_data:
                    log_data.write({
                        'name_of_expenses': rec.expense_id.name_of_expenses,
                        'revised_amount': rec.quantity * rec.rate_per_quantity,
                        'total_amount': rec.expense_id.total_amount,
                        'applied_by': self.env.user.employee_ids.name,
                        'capital_budget_line_id': rec.expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    })
                if not log_data:
                    self.env['kw_revise_budget_action_log'].sudo().create({
                        'name_of_expenses': rec.expense_id.name_of_expenses,
                        'revised_amount': rec.quantity * rec.rate_per_quantity,
                        'total_amount': rec.expense_id.total_amount,
                        'applied_by': self.env.user.employee_ids.name,
                        'capital_budget_line_id': rec.expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    })

    def confirm_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Finance'
            if self.revised_amount_ids and self.for_revise_line:

                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_budget_action_log'].sudo().search(
                        [('capital_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in', ['applied'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': rec.quantity * rec.rate_per_quantity,
                            'total_amount': rec.expense_id.total_amount,
                            'approver_by': self.env.user.employee_ids.name,
                            'capital_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By L2',
                            # 'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_l2',
                        })

    def Cancel_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Cancel'

    def confirm_finance(self):
        if self.pending_at == 'Finance':
            for lines in self.capital_budget_line_ids:
                if not lines.account_code_id:
                    raise ValidationError(f'Account Code is  not set for the expense {lines.name_of_expenses}')
            self.pending_at = 'cfo'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_budget_action_log'].sudo().search(
                        [('capital_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in', ['applied', 'approved_by_l2', 'approved_by_finance'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': rec.quantity * rec.rate_per_quantity,
                            'total_amount': rec.expense_id.total_amount,
                            'approver_by': self.env.user.employee_ids.name,
                            'capital_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By Finance',
                            # 'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_finance',
                        })

    def Cancel_finance(self):
        if self.pending_at == 'Finance':
            self.pending_at = 'Cancel'

    def confirm_cfo(self):
        if self.pending_at == 'cfo':
            # for lines in self.capital_budget_line_ids:
            #     if not lines.account_code_id:
            #         raise ValidationError(f'Account Code is  not set for the expense {lines.name_of_expenses}')
            self.pending_at = 'Approver'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_budget_action_log'].sudo().search(
                        [('capital_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in',
                          ['applied', 'approved_by_l2', 'approved_by_finance', 'approved_by_cfo'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': rec.quantity * rec.rate_per_quantity,
                            'total_amount': rec.expense_id.total_amount,
                            'approver_by': self.env.user.employee_ids.name,
                            'capital_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By Finance(CFO)',
                            # 'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_cfo',
                        })

    def Cancel_cfo(self):
        if self.pending_at == 'cfo':
            self.pending_at = 'Cancel'

    def confirm_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'Validate'
            if self.capital_budget_line_ids and self.for_new_line:
                for line in self.capital_budget_line_ids:
                    line.capital_budget_id = self.capital_budget_id
                    line.state = 'validate'
                    line.id_new_line_bool = True
            if self.revised_amount_ids and self.for_revise_line:
                total_amt = 0.0
                for data in self.revised_amount_ids:

                    line_changes = self.format_revised_amounts(data)
                    log_data = self.env['kw_revise_budget_action_log'].sudo().search(
                        [('capital_budget_line_id', '=', data.expense_id.id),
                         ('name_of_expenses', '=', data.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in', ['applied', 'L2 Approved', 'approved_by_finance'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': data.expense_id.name_of_expenses,
                            'revised_amount': data.quantity * data.rate_per_quantity,
                            'total_amount': data.expense_id.total_amount,
                            'approver_by': self.env.user.employee_ids.name,
                            'capital_budget_line_id': data.expense_id.id,
                            'state': 'Approved',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_approver',
                        })
                    total_amt = data.total_amount + data.apr_budget + data.may_budget + data.jun_budget + data.jul_budget + data.aug_budget + data.sep_budget + data.oct_budget + data.nov_budget + data.dec_budget + data.jan_budget + data.feb_budget + data.mar_budget
                    data.expense_id.write({
                        "date_from": data.date_from,
                        "date_to": data.date_to,
                        "quantity": data.quantity,
                        "rate_per_quantity": total_amt / data.quantity,
                        "total_amount": total_amt,
                        "apr_budget": data.expense_id.apr_budget + data.apr_budget,
                        "may_budget": data.expense_id.may_budget + data.may_budget,
                        "jun_budget": data.expense_id.jun_budget + data.jun_budget,
                        "jul_budget": data.expense_id.jul_budget + data.jul_budget,
                        "aug_budget": data.expense_id.aug_budget + data.aug_budget,
                        "sep_budget": data.expense_id.sep_budget + data.sep_budget,
                        "oct_budget": data.expense_id.oct_budget + data.oct_budget,
                        "nov_budget": data.expense_id.nov_budget + data.nov_budget,
                        "dec_budget": data.expense_id.dec_budget + data.dec_budget,
                        "jan_budget": data.expense_id.jan_budget + data.jan_budget,
                        "feb_budget": data.expense_id.feb_budget + data.feb_budget,
                        "mar_budget": data.expense_id.mar_budget + data.mar_budget,
                        "next_fy_year": data.next_fy_year,
                        "remark": data.remark,
                        "state": 'validate',
                        "id_revise_bool": True
                    })
                    # if data.date_from:
                    #     data.expense_id.date_from = data.date_from
                    # if data.date_to:
                    #     data.expense_id.date_to = data.date_to
                    # if data.quantity:
                    #     data.expense_id.quantity = data.quantity
                    # if data.rate_per_quantity:
                    #     data.expense_id.rate_per_quantity = data.rate_per_quantity
                    #
                    #
                    #
                    # if data.apr_budget:
                    #     data.expense_id.apr_budget = data.apr_budget
                    # if data.may_budget:
                    #     data.expense_id.may_budget = data.may_budget
                    # if data.jun_budget:
                    #     data.expense_id.jun_budget = data.jun_budget
                    # if data.jul_budget:
                    #     data.expense_id.jul_budget = data.jul_budget
                    # if data.aug_budget:
                    #     data.expense_id.aug_budget = data.aug_budget
                    # if data.sep_budget:
                    #     data.expense_id.sep_budget = data.sep_budget
                    # if data.oct_budget:
                    #     data.expense_id.oct_budget = data.oct_budget
                    # if data.nov_budget:
                    #     data.expense_id.nov_budget = data.nov_budget
                    # if data.dec_budget:
                    #     data.expense_id.dec_budget = data.dec_budget
                    # if data.jan_budget:
                    #     data.expense_id.jan_budget = data.jan_budget
                    # if data.feb_budget:
                    #     data.expense_id.feb_budget = data.feb_budget
                    # if data.mar_budget:
                    #     data.expense_id.mar_budget = data.mar_budget
                    # if data.next_fy_year:
                    #     data.expense_id.remark = data.next_fy_year
                    # if data.remark:
                    #     data.expense_id.remark = data.remark
                    #
                    # data.expense_id.total_amount = data.quantity * data.rate_per_quantity

    def cancel_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'Cancel'

    def revert_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'L1'

    def revert_finance(self):
        if self.pending_at == 'Finance':
            self.pending_at = 'L2'

    def revert_cfo(self):
        if self.pending_at == 'cfo':
            self.pending_at = 'Finance'

    def revert_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'cfo'


class RevisedAmount(models.Model):
    _name = 'revised_budget_data'
    _description = 'revised_capital_budget'

    expense_id = fields.Many2one('kw_capital_budget_line')
    month_revies = fields.Selection(string="Month of Revies",
                                    selection=[('April', 'Apr'), ('May', 'May'), ('Jun', 'Jun'),
                                               ('July', 'July'), ('August', 'Aug'),
                                               ('September', 'Sep'), ('October', 'Oct'),
                                               ('November', 'Nov'), ('December', 'Dec'), ('January', 'Jan'),
                                               ('February', 'Feb'), ('March', 'Mar')])
    revised_amount = fields.Float(string='Revise Amount')
    wizard_id = fields.Many2one('revised_budget_wizard', string='Wizard')

    name_of_expenses = fields.Char('Narration')
    quantity = fields.Integer('Quantity')
    rate_per_quantity = fields.Float('Rate per Quantity')
    total_amount = fields.Float('Total Amount')
    date_from = fields.Date('Month Start')
    date_to = fields.Date('Month End')
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
    next_fy_year = fields.Float('Next FY Year')
    remark = fields.Text('Remark')

    # @api.constrains('apr_budget', 'may_budget', 'jun_budget', 'jul_budget', 'aug_budget', 'sep_budget', 'oct_budget',
    #                 'nov_budget', 'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget', 'total_amount')
    # def _check_total_amount(self):
    #     for record in self:
    #         total_budget = record.apr_budget + record.may_budget + record.jun_budget + record.jul_budget + record.aug_budget + record.sep_budget + record.oct_budget + record.nov_budget + record.dec_budget + record.jan_budget + record.feb_budget + record.mar_budget
    #         if total_budget != record.total_amount:
    #             raise ValidationError("Total monthly budgets must be equal to Total Amount.")

    @api.constrains('date_from', 'date_to')
    def date_validate(self):
        for budget in self:
            if budget.date_to < budget.date_from:
                raise ValidationError('Month start date cant be less than end date.')

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget', 'aug_budget', 'sep_budget', 'oct_budget',
                  'nov_budget', 'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget', 'total_amount')
    def get_total_value(self):
        for record in self:
            total = record.apr_budget + record.may_budget + record.jun_budget + record.jul_budget + record.aug_budget + record.sep_budget + record.oct_budget + record.nov_budget + record.dec_budget + record.jan_budget + record.feb_budget + record.mar_budget
            if total != 0.0:
                record.total_amount = total
                print(total, record.total_amount, 'PPPPPPPPPPPPP', total / record.quantity)
                record.rate_per_quantity = total / record.quantity

    # @api.onchange( 'quantity', 'rate_per_quantity')
    # def get_total_value(self):
    #     for rec in self:
    #         rec.total_amount = False
    #         rec.total_amount = rec.quantity * rec.rate_per_quantity


class RevenueCapitalBudgetLinewizard(models.Model):
    _name = 'kw_capital_budget_line_wizard'
    _rec_name = 'name_of_expenses'

    name_of_expenses = fields.Char('Narration', required=True)
    account_code_id = fields.Many2one('account.account', 'Account code')
    amount_required = fields.Float('Amount Required')
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount', )
    wizard_id = fields.Many2one('revised_budget_wizard', string='Wizard')

    # actual_amount = fields.Float(compute='_compute_practical_amount', readonly=True)
    date_from = fields.Date('Month Start')
    date_to = fields.Date('Month End')
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
    next_fy_year = fields.Float('Next FY Year')
    remark = fields.Text('Remark')
    capital_budget_id = fields.Many2one('kw_capital_budget', 'Capital Budget')
    # revised_button_boolean = fields.Boolean(compute='revised_button', store=False)
    revised_attempt_button_visible = fields.Boolean()
    expense_type = fields.Selection(string='Expenses Type',
                                    selection=[('Workorder', 'Workorder'), ('Treasury', 'Treasury')])
    revise_budget_action_log_ids = fields.One2many('kw_revise_budget_action_log', 'capital_budget_line_id',
                                                   'Capital Budget Log')
    quantity = fields.Integer('Quantity')
    rate_per_quantity = fields.Float('Rate per Quantity')
    approved_button_boolean = fields.Boolean()
    revised_button_hide_boolean = fields.Boolean()
    # revised_invisible_button = fields.Boolean(compute='get_button_revised', store=False)
    budgetary_position_id = fields.Many2one('account.budget.post')
    finance_approved_button_boolean = fields.Boolean()
    approver_approved_button_boolean = fields.Boolean()
    approver_reverted_button_boolean = fields.Boolean()
    edit_button_hide_boolean = fields.Boolean()
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
    sequence_ref = fields.Char(string='ID')
    hide_split_button_boolean = fields.Boolean(default=False)


class splltCapitalwizard(models.TransientModel):
    _name = "split_capital_budget_wizard"

    def _get_budget_line_data(self):
        rec = self.env['kw_capital_budget_line'].browse(self.env.context.get('active_ids'))
        return rec

    capital_budget_id = fields.Many2one('kw_capital_budget_line', 'Capital Budget', default=_get_budget_line_data)
    budget_line_ids = fields.One2many('split_capital_budget_wizard_line', 'wiz_id')
    name_of_expenses = fields.Char('Name of expenses', related='capital_budget_id.name_of_expenses')
    date_from = fields.Date('Month Start', related='capital_budget_id.date_from')
    date_to = fields.Date('Month End', related='capital_budget_id.date_to')
    quantity = fields.Integer('Quantity', related='capital_budget_id.quantity')
    rate_per_quantity = fields.Float('Rate per Quantity', related='capital_budget_id.rate_per_quantity')
    apr_budget = fields.Float(related='capital_budget_id.apr_budget')
    may_budget = fields.Float(related='capital_budget_id.may_budget')
    jun_budget = fields.Float(related='capital_budget_id.jun_budget')
    jul_budget = fields.Float(related='capital_budget_id.jul_budget')
    aug_budget = fields.Float(related='capital_budget_id.aug_budget')
    sep_budget = fields.Float(related='capital_budget_id.sep_budget')
    oct_budget = fields.Float(related='capital_budget_id.oct_budget')
    nov_budget = fields.Float(related='capital_budget_id.nov_budget')
    dec_budget = fields.Float(related='capital_budget_id.dec_budget')
    jan_budget = fields.Float(related='capital_budget_id.jan_budget')
    feb_budget = fields.Float(related='capital_budget_id.feb_budget')
    mar_budget = fields.Float(related='capital_budget_id.mar_budget')
    total_amount = fields.Float(related='capital_budget_id.total_amount')
    account_code_id = fields.Many2one('account.account', 'Account code', related='capital_budget_id.account_code_id')
    remark = fields.Text(related='capital_budget_id.remark')

    def split_capital_budget(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_capital_budget_line'].sudo().search([('id', '=', active_ids)])
        capital_budget_line = self.env['kw_capital_budget_line'].sudo().browse(active_ids)
        total_amount = capital_budget_line.total_amount
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
            if capital_budget_line.sequence_ref and str(capital_budget_line.sequence_ref).isdigit():
                dataa = self.env['kw_capital_budget_line'].sudo().search(
                    [('capital_budget_id', '=', capital_budget_line.capital_budget_id.id)])
                alp = []
                for recc in dataa:
                    import re
                    pattern = r'\d+'
                    numbers = re.findall(pattern, recc.sequence_ref)
                    int_numbers = [int(num) for num in numbers]
                    if int_numbers:
                        if not str(recc.sequence_ref).isdigit() and str(
                                int_numbers[0]) == capital_budget_line.sequence_ref:
                            alp.append(recc.sequence_ref[-1])
                if len(alp) > 0:
                    numeric_part = capital_budget_line.sequence_ref
                    sorted_alp = sorted(alp)
                    alpha = sorted_alp[-1]
                    next_alpha = chr(ord(alpha) + 1)
                    new_value = f"{numeric_part}{next_alpha}"
                else:
                    numeric_part = capital_budget_line.sequence_ref
                    alpha_part = ''
                    next_alpha = 'A'
                    new_value = f"{numeric_part}{next_alpha}"

            new_budget_line = self.env['kw_capital_budget_line'].sudo().create(
                {'name_of_expenses': rec.name_of_expenses,
                 'date_from': rec.date_from,
                 'date_to': rec.date_to,
                 'quantity': rec.quantity,
                 'total_amount': rec.total_amount,
                 'rate_per_quantity': rec.rate_per_quantity,
                 'account_code_id': rec.account_code_id.id,
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

                 'remark': rec.remark,
                 'capital_budget_id': data.capital_budget_id.id,
                 'state': 'validate',
                 'sequence_ref': new_value,
                 'hide_split_button_boolean': True,
                 'revised_button_hide_boolean': True
                 })
        data.write({
            month: capital_budget_line[month] - new_monthly_amounts[month]
            for month in month_budget_sums
        })
        data.write({'total_amount': total_amount - sum(new_monthly_amounts.values()),
                    'rate_per_quantity': (total_amount - sum(month_budget_sums.values())) / (
                        capital_budget_line.quantity if capital_budget_line.quantity else 1)})


class SplitCapitalWizardline(models.TransientModel):
    _name = 'split_capital_budget_wizard_line'
    _description = 'Split Button Wizard'

    wiz_id = fields.Many2one('split_capital_budget_wizard')
    name_of_expenses = fields.Char('Narration', required=True)
    account_code_id = fields.Many2one('account.account', 'Account code')
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
    remark = fields.Text('Remark')
    date_from = fields.Date('Month Start', required=True)
    date_to = fields.Date('Month End', required=True)
    quantity = fields.Integer('Quantity')
    rate_per_quantity = fields.Float('Rate per Quantity')

    @api.onchange('quantity', 'rate_per_quantity')
    def get_total_value(self):
        for rec in self:
            rec.total_amount = False
            rec.total_amount = rec.quantity * rec.rate_per_quantity

    @api.constrains('apr_budget', 'may_budget', 'jun_budget', 'jul_budget', 'aug_budget', 'sep_budget', 'oct_budget',
                    'nov_budget', 'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget', 'total_amount')
    def _check_total_amount(self):
        for record in self:
            total_budget = record.apr_budget + record.may_budget + record.jun_budget + record.jul_budget + record.aug_budget + record.sep_budget + record.oct_budget + record.nov_budget + record.dec_budget + record.jan_budget + record.feb_budget + record.mar_budget
            if total_budget != record.total_amount:
                raise ValidationError("Total monthly budgets must be equal to Total Amount.")

