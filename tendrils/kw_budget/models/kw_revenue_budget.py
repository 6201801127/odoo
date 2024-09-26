from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime
import base64
# import openpyxl, mimetypes
from io import BytesIO
import ast
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


class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    @api.model
    def _find_allowed_model_wise(self, doc_model, doc_dict):
        doc_ids = list(doc_dict)
        allowed_doc_ids = self.env[doc_model].with_context(active_test=False).search([('id', 'in', doc_ids)]).ids
        print(allowed_doc_ids, doc_ids, doc_dict, doc_model)
        print(set([message_id for allowed_doc_id in doc_ids for message_id in doc_dict[allowed_doc_id]]), 'vvvvvvvvvvv')
        msg = set([message_id for allowed_doc_id in doc_ids for message_id in doc_dict[allowed_doc_id]])
        return msg


class AccountingRevenueBudget(models.Model):
    _name = 'kw_revenue_budget'
    _description = "Revenue Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "fiscal_year_id"

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    def _get_department_user(self):
        domain = [('id', '=', 0)]
        user = self.env.user.employee_ids
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        if user:
            domain = []
            budget_department_id = self.env['kw_budget_dept_mapping'].search([
                '|', ('level_2_approver.id', '=', user.id),
                ('level_1_approver.id', '=', user.id),
                ('fiscal_year', '=', current_fiscal.id), ('state', '=', 'approve')])
            if budget_department_id:
                department_ids = [department.id for department in budget_department_id if
                                  department.revenue_boolean == True]
                domain = [('id', 'in', department_ids)]
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
    revenue_budget_line_ids = fields.One2many('kw_revenue_budget_line', 'revenue_budget_id', 'Revenue Budget Lines',
                                              copy=True)
    division_id = fields.Many2one('hr.department', 'Division', readonly=True,
                                  default=lambda self: self.get_self_emp_division_details())
    section_id = fields.Many2one('hr.department', 'Section', readonly=True, default=lambda self: self.get_emp_section())
    branch_id = fields.Many2one('kw_res_branch', 'Branch', readonly=True, default=lambda self: self.get_branch_id())
    rb_pending_at = fields.Char(string="Pending At")
    budget_department = fields.Many2one('kw_budget_dept_mapping', 'Budget For', track_visibility='always',
                                        domain=_get_department_user)
    budget_dept = fields.Many2one('hr.department', 'Department', related='budget_department.department_id')
    budget_division = fields.Many2one('hr.department', 'Division', related='budget_department.division_id')
    budget_section = fields.Many2one('hr.department', 'Section', related='budget_department.section_id')
    pending_at_ids = fields.Many2many('hr.employee', string='Pending at')
    pending_at_fixed_ids = fields.Many2many('hr.employee', 'hr_employee_pending_at_fixed_rel', string='Pending at')
    # pending_at_fixed_ids = fields.Many2many('hr.employee', 'hr_employee_pending_at_fixed_rel', string='Pending at')
    revise_revenue_action_log_ids = fields.One2many('kw_revise_revenue_budget_action_log', 'revenue_budget_id',
                                                    'Revenue Budget Log')
    approver_head_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    revenue_revised_finance_approval_boolean = fields.Boolean()
    revenue_revised_approver_approval_boolean = fields.Boolean()
    revised_amount = fields.Float()
    revised_month = fields.Char()
    add_expense_line_hide_boolean = fields.Boolean()
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self._get_user_currency())
    finance_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    finance_cfo_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    approver_revert_back_boolean = fields.Boolean(compute='get_boolean_all', store=False)
    file = fields.Binary(string='Upload File>>', attachment=True)
    generate_seq_boolean = fields.Boolean(string='Generate Sequence Boolean')
    for_new_line_revised = fields.Selection([
        ('draft_blank', ''),
        ('new_line', 'Add Budget New Lines'),
        ('Revise', 'Revise Budget lines')
    ], 'For new/revise budget', default='draft_blank', required=True, track_visibility='always')
    active_id_budget = fields.Integer('ID', default=lambda self: self.env['kw_revenue_budget'].sudo().search(
        [('id', '=', self.env.context.get('active_id'))]))
    take_action_view_bool = fields.Boolean('Boolean', compute='_get_bool_enable')
    pending_since = fields.Datetime('Pending Since', default=datetime.now(), compute='_get_pending_since')

    @api.depends('state')
    def _get_pending_since(self):
        for rec in self:
            if rec.state:
                rec.pending_since = datetime.now()
            else:
                self.pending_since = ''

    def _get_bool_enable(self):
        print(self.env.context)
        if self.env.context.get('take_action_view_bool'):
            self.take_action_view_bool = True
        else:
            self.take_action_view_bool = False

    def open_revise_wizard(self):

        return {
            'name': 'Revised Revenue Budget Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'revised_revenue_budget_wizard',
            'view_id': self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id,
            'target': 'new',
            'context': {
                'default_revenue_budget_id': self.id,
                'kw_revise_wizard': True
                # 'default_existing_revenue_budget_line_ids': new_lines,
            },
        }

    # invisible = "context.get('logical_value',False)"

    # @api.constrains('fiscal_year_id', 'budget_department')
    # def _check_duplicate_revenue_budget(self):
    #     existing_record = self.search([
    #         ('fiscal_year_id', '=', self.fiscal_year_id.id),
    #         ('budget_department', '=', self.budget_department.id),
    #         ('state', 'not in', ['cancel'])
    #     ])
    #     if existing_record:
    #         raise ValidationError("A record for this fiscal year already exists.")

    # @api.constrains('fiscal_year_id','revenue_budget_line_ids')
    # def _validate_budget_details(self):
    #     for budget in self:
    #         if budget.fiscal_year_id and not budget.revenue_budget_line_ids:
    #             raise ValidationError('Please add Budget details.')

    @api.model
    def _get_user_currency(self):
        if self.env.user.company_id:
            return self.env.user.company_id.currency_id.id

    def get_boolean_all(self):
        for rec in self:
            rec.approver_head_boolean = True if rec.state in (
                'to_approve') and self.env.user.employee_ids.id in rec.budget_department.level_2_approver.ids else False
            rec.finance_revert_back_boolean = True if rec.state == 'approved' and self.env.user.has_group(
                'kw_budget.group_finance_kw_budget') else False
            rec.finance_cfo_revert_back_boolean = True if rec.state == 'cfo' and self.env.user.has_group(
                'kw_budget.group_cfo_kw_budget') else False
            rec.approver_revert_back_boolean = True if rec.state == 'confirm' and self.env.user.has_group(
                'kw_budget.group_approver_kw_budget') else False

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

    def apply_revenue_budget(self):
        for rec in self:
            if rec.fiscal_year_id and not rec.revenue_budget_line_ids:
                raise ValidationError('Please add Budget details.')
            if self.env.user.employee_ids.id in rec.budget_department.level_2_approver.ids:
                finance_group = self.env.ref(
                    'kw_budget.group_finance_kw_budget')
                finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                if not finance_users:
                    raise ValidationError("No users found in the finance group.")
                approver_ids = finance_users.mapped('employee_ids.id')
                rec.write({'state': 'approved',
                           'pending_at_ids': [(6, 0, approver_ids)]})
                for recc in rec.revenue_budget_line_ids:
                    recc.state = 'to_approve'
            else:
                approver_ids = rec.budget_department.level_2_approver.ids
                rec.write({'state': 'to_approve',
                           'pending_at_ids': [(6, 0, approver_ids)]

                           })
                for recc in rec.revenue_budget_line_ids:
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
            for recc in rec.revenue_budget_line_ids:
                recc.state = 'to_approve'

    @api.multi
    def action_budget_validate_cfo(self):
        approver_group = self.env.ref(
            'kw_budget.group_approver_kw_budget')
        approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        if not approver_users:
            raise ValidationError("No users found in the approver group.")
        approver_ids = approver_users.mapped('employee_ids.id')
        for rec in self:
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                for recc in rec.revenue_budget_line_ids:
                    if not recc.account_code_id:
                        raise ValidationError(f'Account Code is  not set for the expense {recc.name_of_expenses}')
            rec.write({'state': 'confirm',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.revenue_budget_line_ids:
                recc.state = 'confirm'

    @api.multi
    def action_budget_validate(self):
        cfo_group = self.env.ref(
            'kw_budget.group_cfo_kw_budget')
        cfo_users = self.env['res.users'].search([('groups_id', 'in', cfo_group.id)])
        if not cfo_users:
            raise ValidationError("No users found in the CFO group.")
        approver_ids = cfo_users.mapped('employee_ids.id')
        for rec in self:
            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                for recc in rec.revenue_budget_line_ids:
                    if not recc.account_code_id:
                        raise ValidationError(f'Account Code is  not set for the expense {recc.name_of_expenses}')
            rec.write({'state': 'cfo',
                       'pending_at_ids': [(6, 0, approver_ids)]})
            for recc in rec.revenue_budget_line_ids:
                recc.state = 'confirm'

    def action_budget_revert_back(self):
        for rec in self:
            rec.write({'state': 'draft',
                       'add_expense_line_hide_boolean': False,
                       'pending_at_ids': [(6, 0, [])]})
            for recc in rec.revenue_budget_line_ids:
                recc.revised_button_hide_boolean = False
                recc.state = 'draft'

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
            for recc in rec.revenue_budget_line_ids:
                recc.revised_button_hide_boolean = True
                recc.state = 'validate'

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user.employee_ids
        l2_ids = []
        l1_ids = []
        if self._context.get('take_action_revenue_budget'):
            l1_budget_obj = []
            l2_budget_obj = []
            budget_department_id = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_2_approver.id', '=', user.id)])
            if budget_department_id:
                if len(budget_department_id) == 1:
                    query = "select id from kw_revenue_budget where state = 'to_approve' and budget_department = " + str(
                        budget_department_id.id)
                if len(budget_department_id) > 1:
                    query = "select id from kw_revenue_budget where state = 'to_approve' and  budget_department in " + str(
                        tuple(budget_department_id.ids))
                self._cr.execute(query)
                ids = self._cr.fetchall()
                if ids:
                    l2_ids = [x[0] for x in ids]
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_revenue_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_revenue_budget where budget_department in " + str(
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
                        FROM kw_revenue_budget
                        WHERE state = 'confirm'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_revenue_budget
                                WHERE state = 'cfo'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    cfo_budget_obj = [data[0] for data in lines_obj]

                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_revenue_budget
                                WHERE state = 'approved'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + cfo_budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                finance_budget_obj = []
                query = """
                        SELECT id
                        FROM kw_revenue_budget
                        WHERE state = 'cfo'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                # print(budget_obj, 'approver')
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    query = """
                                SELECT id
                                FROM kw_revenue_budget
                                WHERE state = 'approved'
                            """
                    self._cr.execute(query)
                    lines_obj = self._cr.fetchall()
                    finance_budget_obj = [data[0] for data in lines_obj]

                budget_obj = budget_obj + finance_budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)

            elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                        SELECT id
                        FROM kw_revenue_budget
                        WHERE state = 'approved'
                    """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                budget_obj = [data[0] for data in lines_obj]
                budget_obj = budget_obj + l1_ids + l2_ids
                args = [('id', 'in', budget_obj)]
                return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)
            elif self.env.user.has_group('kw_budget.group_l2_kw_budget'):

                budget_obj = l2_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)
            else:
                budget_obj = l1_ids
                print(budget_obj, 'budget_objbudget_objbudget_obj')
                args = [('id', 'in', budget_obj)]
                return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                    count=count, access_rights_uid=access_rights_uid)
        # take_action_sbu_budget
        elif self._context.get('take_action_view_bool'):
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_revenue_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_revenue_budget where budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)

        elif self._context.get('treasury_budget_create'):
            l1_ids = []
            budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
                ('level_1_approver.id', '=', user.id)])
            if budget_department_id_l1:
                if len(budget_department_id_l1) == 1:
                    l1query = "select id from kw_revenue_budget where budget_department = " + str(
                        budget_department_id_l1.id)
                if len(budget_department_id_l1) > 1:
                    l1query = "select id from kw_revenue_budget where budget_department in " + str(
                        tuple(budget_department_id_l1.ids))
                self._cr.execute(l1query)
                l1_ids = self._cr.fetchall()
                if l1_ids:
                    l1_ids = [x[0] for x in l1_ids]
            budget_obj = []
            budget_obj = l1_ids
            args = [('id', 'in', budget_obj)]
            return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)


        elif self._context.get('view_status_revenue_budget'):
            if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
                args += ['|', ('create_uid', '=', self.env.user.id), '&',
                         ('budget_department.level_2_approver', 'in', self.env.user.employee_ids.ids),
                         ('state', 'not in', ['draft'])]
            elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group(
                    'kw_budget.group_approver_kw_budget') or self.env.user.has_group(
                'kw_budget.group_manager_kw_budget'):
                args += [('state', 'not in', ['draft'])]
            return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count, access_rights_uid=access_rights_uid)

        return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count, access_rights_uid=access_rights_uid)

    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('take_action_revenue_budget'):
    #         if self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_approver_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_cfo_kw_budget'):
    #             args += ['|', ('pending_at_ids', 'in', self.env.user.employee_ids.id),
    #                      ('revenue_revised_approver_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_finance_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_cfo_kw_budget'):
    #             args += ['|', '|', ('state', 'in', ['approved', 'confirm', 'cfo']),
    #                      ('revenue_revised_finance_approval_boolean', '=', True), '|',
    #                      ('state', 'in', ['approved', 'confirm', 'cfo']),
    #                      ('revenue_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_finance_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_cfo_kw_budget'):
    #             args += ['|', '&', ('state', 'in', ['to_approve', 'cfo']),
    #                      ('pending_at_ids', 'in', self.env.user.employee_ids.id), '|',
    #                      ('state', 'in', ['approved', 'confirm']),
    #                      ('revenue_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget') and self.env.user.has_group(
    #                 'kw_budget.group_cfo_kw_budget'):
    #             args += ['|', ('state', 'in', ['cfo']),
    #                      ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             user = self.env.user.employee_ids
    #             if user:
    #                 budget_department_id = self.env['kw_budget_dept_mapping'].search([
    #                     ('level_2_approver.id', '=', user.id)])
    #                 if budget_department_id:
    #                     if len(budget_department_id) == 1:
    #                         query = "select id from kw_revenue_budget where budget_department = " + str(
    #                             budget_department_id.id)
    #                     if len(budget_department_id) > 1:
    #                         query = "select id from kw_revenue_budget where budget_department in " + str(
    #                             tuple(budget_department_id.ids))
    #                     self._cr.execute(query)
    #                     ids = self._cr.fetchall()
    #             args += [('state', 'in', ['to_approve', 'validate']),
    #                      ('pending_at_ids', 'in', self.env.user.employee_ids.id), ('id', 'in', ids)]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             args += ['|', ('state', 'in', ['approved', 'confirm']),
    #                      ('revenue_revised_finance_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #             args += ['|', ('state', 'in', ['confirm']), ('revenue_revised_approver_approval_boolean', '=', True)]
    #         elif self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
    #             args += ['|', ('state', 'in', ['cfo']), ('pending_at_ids', 'in', self.env.user.employee_ids.id)]
    #         elif self.env.user.has_group('kw_budget.group_manager_kw_budget'):
    #             return []
    #     elif self._context.get('view_status_revenue_budget'):
    #         if self.env.user.has_group('kw_budget.group_department_head_kw_budget'):
    #             args += ['|', ('create_uid', '=', self.env.user.id), '&',
    #                      ('budget_department.level_2_approver', 'in', self.env.user.employee_ids.ids),
    #                      ('state', 'not in', ['draft'])]
    #         elif self.env.user.has_group('kw_budget.group_finance_kw_budget') or self.env.user.has_group(
    #                 'kw_budget.group_approver_kw_budget') or self.env.user.has_group(
    #                 'kw_budget.group_manager_kw_budget'):
    #             args += [('state', 'not in', ['draft'])]
    #
    #     return super(AccountingRevenueBudget, self)._search(args, offset=offset, limit=limit, order=order, count=count,
    #                                                         access_rights_uid=access_rights_uid)

    def get_new_line_view(self):
        view_id = self.env.ref("kw_budget.kw_kw_revenue_budget_form_new_line").id
        action = {
            'name': 'Add Budget Expense',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_revenue_budget',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {}
        }
        return action

    # def open_revise_wizard(self):
    #     # if self.for_new_line_revised == 'Revise':
    #     #     budget_id = self.active_id_budget
    #         # self.unlink()
    #         return {
    #             'name': 'Revised Revenue Budget Wizard',
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'revised_revenue_budget_wizard',
    #             'view_id': self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id,
    #             'target': 'new',
    #             'context': {
    #                 # 'default_revenue_expense_id': rec.id,
    #                 # 'default_revenue_budget_id': self.id,
    #                 # 'default_name_of_expenses': rec.name_of_expenses,
    #                 # 'default_expense_type': rec.expense_type,
    #                 # 'default_revised_amount_ids': default_revised_amount_ids,
    #             },
    #         }

    def revenue_revised_add_line_submit(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_revenue_budget'].sudo().search([('id', '=', active_ids)])
        for rec in self.revenue_budget_line_ids:
            rec.revenue_budget_id = active_ids
            rec.state = 'to_approve'
            rec.edit_button_hide_boolean = True
            rec.l2_approve_button_boolean = True
            data.revenue_revised_finance_approval_boolean = True
            rec.finance_approved_button_boolean = False
            rec.revised_button_hide_boolean = False
            data.add_expense_line_hide_boolean = False
            approver_ids = data.budget_department.level_2_approver.ids
            data.write({'pending_at_ids': [(6, 0, approver_ids)]

                        })
        self.unlink()

    @api.multi
    def generate_xls_format(self):
        self.ensure_one()
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        result_url = f"{base_url}/download-xls-format/"
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of XLS format",
            'url': result_url
        }

    def generate_budget_line(self):
        for rec in self:
            if not rec.file:
                raise ValidationError('Please Upload File')

            excel_data = BytesIO(base64.b64decode(rec.file))
            work_book = openpyxl.load_workbook(excel_data)
            worksheet = work_book.active

            budget_lines = []
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if row[1].capitalize() not in ['Expenses', 'Income']:
                    raise ValidationError(f'Column data {row[1]} do not match the upload format')
                total = sum(r if r else 0 for r in row[2:14])
                budget_lines.append((0, 0, {
                    'name_of_expenses': row[0],
                    'expense_type': row[1].capitalize(),
                    'apr_budget': row[2],
                    'may_budget': row[3],
                    'jun_budget': row[4],
                    'jul_budget': row[5],
                    'aug_budget': row[6],
                    'sep_budget': row[7],
                    'oct_budget': row[8],
                    'nov_budget': row[9],
                    'dec_budget': row[10],
                    'jan_budget': row[11],
                    'feb_budget': row[12],
                    'mar_budget': row[13],
                    'total_amount': total,
                    'remark': row[14],
                }))
            rec.revenue_budget_line_ids = budget_lines
            self.file = False

    file_name = fields.Char("File Name")

    @api.constrains('file')
    def _check_file_extension(self):
        for record in self:
            if record.file:
                file_name = record.file_name or ''
                file_extension = mimetypes.guess_extension(mimetypes.guess_type(file_name)[0])
                if file_extension != '.xlsx':
                    raise ValidationError("Please upload only XLSX files.")

    def action_budget_generate_id(self):
        # if not self.generate_seq_boolean:

        params = self.env['ir.config_parameter'].sudo()
        count = params.get_param('id_count_revenue')

        line_data = self.env['kw_revenue_budget_line'].sudo().search(
            [('state', '=', 'validate'), ('revenue_budget_id.fiscal_year_id', '=', self.fiscal_year_id.id)])
        sequence_map = {}

        for rec in line_data:
            department_name = rec.revenue_budget_id.budget_department.name
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

                if not rec.sequence_ref:
                    sequence_number_copy = sequence_number
                    if rec.id_new_line_bool:
                        sequence_number_copy = 'A' + str(sequence_number_copy)
                        if rec.id_revise_bool:
                            sequence_number_copy = 'R' + str(sequence_number_copy)
                        params.set_param('id_count_revenue', sequence_number)
                        sequence_number += 1

                    elif rec.id_revise_bool:
                        sequence_number_copy = 'R' + str(sequence_number_copy)

                        params.set_param('id_count_revenue', sequence_number)
                        sequence_number += 1
                    else:
                        sequence_number_copy = sequence_number_copy
                        params.set_param('id_count_revenue', sequence_number)
                        sequence_number += 1
                rec.sequence_ref = sequence_number_copy

        # self.generate_seq_boolean =True

    def print_treasury_report(self):
        '''
        this function is used to print the XLXS report
        '''

        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'Treasury Budget.xlsx')
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
        worksheet.merge_range(row, col, row, col + 17, "Treasury Budget", style_header)
        row += 1
        worksheet.write(row, col, 'sr.No ', style_header2)
        worksheet.write(row, col + 1, 'ID', style_header2)
        worksheet.write(row, col + 2, 'Name Of Expenses', style_header2)
        worksheet.write(row, col + 3, 'Head Of Expenses', style_header2)
        worksheet.write(row, col + 4, 'April', style_header2)
        worksheet.write(row, col + 5, 'May', style_header2)
        worksheet.write(row, col + 6, 'June', style_header2)
        worksheet.write(row, col + 7, 'July', style_header2)
        worksheet.write(row, col + 8, 'August', style_header2)
        worksheet.write(row, col + 9, 'September', style_header2)
        worksheet.write(row, col + 10, 'October ', style_header2)
        worksheet.write(row, col + 11, 'November ', style_header2)
        worksheet.write(row, col + 12, 'December ', style_header2)
        worksheet.write(row, col + 13, 'January ', style_header2)
        worksheet.write(row, col + 14, 'Feburary ', style_header2)
        worksheet.write(row, col + 15, 'March ', style_header2)
        worksheet.write(row, col + 16, 'Total Amount', style_header2)
        worksheet.write(row, col + 17, 'Remarks', style_header2)

        if self:
            apr, may, june, july, aug, sep, oct, nov, dec, jan, feb, mar, total = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            seq = 1
            for lines in self.revenue_budget_line_ids:
                row += 1

                print(lines, 'single linee')
                worksheet.write(row, col, seq, style_data)
                worksheet.write(row, col + 1, lines.sequence_ref, style_data)
                worksheet.write(row, col + 2, lines.name_of_expenses or '', style_data)
                worksheet.write(row, col + 3, lines.expense_type, style_data)
                worksheet.write(row, col + 4, lines.apr_budget, style_data)
                worksheet.write(row, col + 5, lines.may_budget, style_data)
                worksheet.write(row, col + 6, lines.jun_budget, style_data)
                worksheet.write(row, col + 7, lines.jul_budget or '', style_data)
                worksheet.write(row, col + 8, lines.aug_budget or '', style_data)
                worksheet.write(row, col + 9, lines.sep_budget, style_data)
                worksheet.write(row, col + 10, lines.oct_budget, style_data)
                worksheet.write(row, col + 11, lines.nov_budget, style_data)
                worksheet.write(row, col + 12, lines.dec_budget, style_data)
                worksheet.write(row, col + 13, lines.jan_budget, style_data)
                worksheet.write(row, col + 14, lines.feb_budget, style_data)
                worksheet.write(row, col + 15, lines.mar_budget, style_data)
                worksheet.write(row, col + 16, lines.total_amount, style_data2)
                worksheet.write(row, col + 17, lines.remark, style_data)
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
                seq += 1
            row += 1
            worksheet.write(row, col + 4, apr, style_data3)
            worksheet.write(row, col + 5, may, style_data3)
            worksheet.write(row, col + 6, june, style_data3)
            worksheet.write(row, col + 7, july or '', style_data3)
            worksheet.write(row, col + 8, aug or '', style_data3)
            worksheet.write(row, col + 9, sep, style_data3)
            worksheet.write(row, col + 10, oct, style_data3)
            worksheet.write(row, col + 11, nov, style_data3)
            worksheet.write(row, col + 12, dec, style_data3)
            worksheet.write(row, col + 13, jan, style_data3)
            worksheet.write(row, col + 14, feb, style_data3)
            worksheet.write(row, col + 15, mar, style_data3)
            worksheet.write(row, col + 16, total, style_data3)

        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "Treasury Budget.xlsx"
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


class RevenueBudgetLine(models.Model):
    _name = 'kw_revenue_budget_line'
    _rec_name = 'name_of_expenses'

    name_of_expenses = fields.Char('Name of expenses', required=True)
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
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount')
    remark = fields.Text('Remark')
    revenue_budget_id = fields.Many2one('kw_revenue_budget', 'Revenue Budget')
    revenue_budget_revise = fields.Many2one('revised_revenue_budget_wizard', 'Revenue Budget suppor id')
    expense_type = fields.Selection(string='Head of Expenses',
                                    selection=[('Income', 'Income'), ('Expenses', 'Expenses')])
    revise_revenue_action_log_ids = fields.One2many('kw_revise_revenue_budget_action_log', 'revenue_budget_line_id',
                                                    'Revenue Budget Log')
    finance_approved_button_boolean = fields.Boolean()
    approver_approved_button_boolean = fields.Boolean()
    approver_reverted_button_boolean = fields.Boolean()
    revised_button_hide_boolean = fields.Boolean()
    edit_button_hide_boolean = fields.Boolean()
    budgetary_position_id = fields.Many2one('account.budget.post')
    l2_approve_button_boolean = fields.Boolean()
    # actual_amount = fields.Float('Actual Amount', compute="_compute_practical_amount", readonly=True)
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
    currency_id = fields.Many2one('res.currency', related='revenue_budget_id.currency_id')
    sequence_ref = fields.Char(string='ID')
    hide_split_button_boolean = fields.Boolean(default=False)
    id_revise_bool = fields.Boolean(default=False)
    id_new_line_bool = fields.Boolean(default=False)

    # @api.multi
    # def _compute_practical_amount(self):
    #     for line in self:
    #         acc_ids = line.budgetary_position_id.account_ids.ids
    #         date_to = line.revenue_budget_id.fiscal_year_id.date_stop
    #         date_from = line.revenue_budget_id.fiscal_year_id.date_start
    #         aml_obj = self.env['account.move.line']
    #         domain = [('account_id', '=',
    #                    line.account_code_id.id),
    #                   ('date', '>=', date_from),
    #                   ('date', '<=', date_to)
    #                   ]
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
    #                         ('date', '>=', self.revenue_budget_id.fiscal_year_id.date_start),
    #                         ('date', '<=', self.revenue_budget_id.fiscal_year_id.date_stop)
    #                         ]
    #     return action

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

    def approve_revised_budget_l2(self):
        if self.state == "to_approve":
            if self.l2_approve_button_boolean:
                finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
                finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                if not finance_users:
                    raise ValidationError("No users found in the finance group.")
                approver_ids = finance_users.mapped('employee_ids.id')

                # check other l2 pending lines
                l2_pending_line = self.env['kw_revenue_budget_line'].search(
                    [('revenue_budget_id', '=', self.revenue_budget_id.id), ('l2_approve_button_boolean', '=', True),
                     ('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                if l2_pending_line:
                    l2_approver_ids = self.revenue_budget_id.budget_department.level_2_approver.ids
                    if l2_approver_ids:
                        approver_ids = approver_ids + l2_approver_ids
                        approver_ids = list(dict.fromkeys(approver_ids))

                for rec in self:
                    rec.revenue_budget_id.pending_at_ids = [(6, 0, approver_ids)]
                self.finance_approved_button_boolean = True
                self.l2_approve_button_boolean = False
                self.revenue_budget_id.revenue_revised_finance_approval_boolean = True
        if self.state == 're_apply':
            finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
            finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
            if not finance_users:
                raise ValidationError("No users found in the finance group.")
            approver_ids = finance_users.mapped('employee_ids.id')
            # check other l2 pending lines
            l2_pending_line = self.env['kw_revenue_budget_line'].search(
                [('revenue_budget_id', '=', self.revenue_budget_id.id), ('l2_approve_button_boolean', '=', True),
                 ('state', 'in', ('to_approve', 're_apply')), ('id', '!=', self.id)])
            if l2_pending_line:
                l2_approver_ids = self.revenue_budget_id.budget_department.level_2_approver.ids
                if l2_approver_ids:
                    approver_ids = approver_ids + l2_approver_ids
                    approver_ids = list(dict.fromkeys(approver_ids))
            for rec in self:
                rec.revenue_budget_id.pending_at_ids = [(6, 0, approver_ids)]
            self.finance_approved_button_boolean = True
            self.l2_approve_button_boolean = False
            self.revenue_budget_id.revenue_revised_finance_approval_boolean = True

    def approve_revised_budget_l2_reject(self):
        if self.state == "to_approve":
            if self.l2_approve_button_boolean:
                self.finance_approved_button_boolean = False
                self.l2_approve_button_boolean = False
                self.state = 'cancel'
            if self.state == 're_apply':
                self.finance_approved_button_boolean = False
                self.l2_approve_button_boolean = False
                self.state = 'cancel'

    def approve_revised_revenue_budget(self):
        for rec in self:
            log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                [('revenue_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.finance_approved_button_boolean = False
                    rec.edit_button_hide_boolean = False
                    rec.state = 're_f_approved'
                    rec.approver_approved_button_boolean = True
                    rec.revenue_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view

                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state in ['to_approve', 're_apply']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        # rec.approver_approved_button_boolean = True
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False  # record for search view
                        # rec.revenue_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view
                        approver_group = self.env.ref(
                            'kw_budget.group_approver_kw_budget')
                        approver_group_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
                        if not approver_group_users:
                            raise ValidationError("No users found in the approver group.")
                        approver_ids = approver_group_users.mapped('employee_ids.id')
                        rec.revenue_budget_id.pending_at_ids = [(6, False, approver_ids)]
                    if len(val) != 0:
                        finance_users = False
                        pending_finance_lines = self.env['kw_revenue_budget_line'].search(
                            [('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id),
                             ('l2_approve_button_boolean', '=', False),
                             ('revenue_budget_id', '=', rec.revenue_budget_id.id),
                             ('finance_approved_button_boolean', '=', True)])
                        if not pending_finance_lines:
                            rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False
                        if pending_finance_lines:
                            finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
                            finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                            if finance_users:
                                finance_users = finance_users.mapped('employee_ids.id')
                                # approver_ids = approver_ids + finance_users_ids
                                # approver_ids = list(dict.fromkeys(approver_ids))
                        # check other l2 pending lines
                        l2_pending_line = self.env['kw_revenue_budget_line'].search(
                            [('revenue_budget_id', '=', self.revenue_budget_id.id),
                             ('l2_approve_button_boolean', '=', True),
                             ('state', '=', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                        if l2_pending_line:
                            l2_approver_ids = self.revenue_budget_id.budget_department.level_2_approver.ids
                            if l2_approver_ids:
                                if finance_users:
                                    approver_ids = finance_users + l2_approver_ids
                                    approver_ids = list(dict.fromkeys(approver_ids))
                                else:
                                    approver_ids = l2_approver_ids
                            else:
                                approver_ids = finance_users
                        else:
                            approver_ids = finance_users

                        rec.revenue_budget_id.pending_at_ids = [(6, False, approver_ids)]

                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Finance Approved',
                        'approve_date': date.today(),
                        'revise_budget_status': 'approved_by_finance',
                    })
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):

                    approver_ids = False
                    l2_pending_line = self.env['kw_revenue_budget_line'].search(
                        [('revenue_budget_id', '=', self.revenue_budget_id.id),
                         ('l2_approve_button_boolean', '=', True),
                         ('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                    if l2_pending_line:
                        l2_approver_ids = self.revenue_budget_id.budget_department.level_2_approver.ids
                        if l2_approver_ids:
                            approver_ids = l2_approver_ids
                    finance_pending = self.env['kw_revenue_budget_line'].search(
                        [('revenue_budget_id', '=', self.revenue_budget_id.id),
                         ('finance_approved_button_boolean', '=', True),
                         ('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                    if not finance_pending:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False
                    if finance_pending:
                        finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
                        finance_group_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                        if finance_group_users:
                            finance_users = finance_group_users.mapped('employee_ids.id')
                            if approver_ids:
                                approver_ids = approver_ids + finance_users
                                approver_ids = list(dict.fromkeys(approver_ids))

                    rec.revenue_budget_id.pending_at_ids = approver_ids
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    # data = self.env['revised_revenue_budget_wizard'].search([('revenue_budget_id', '=', rec.revenue_budget_id.id), ('revised_amount_ids.expense_id', '=', rec.id)],limit=1)
                    data = self.env['revised_revenue_budget_data'].search([('expense_id', '=', rec.id)],
                                                                          order="id desc", limit=1)
                    # rec.expense_type = data.expense_type
                    # rec.remark = data.remark
                    rec.state = 'validate'
                    if data.apr_budget:
                        rec.apr_budget = rec.apr_budget + data.apr_budget

                    if data.may_budget:
                        rec.may_budget = rec.may_budget + data.may_budget
                    if data.jun_budget:
                        rec.jun_budget = rec.jun_budget + data.jun_budget
                    if data.jul_budget:
                        rec.jul_budget = rec.jul_budget + data.jul_budget
                    if data.aug_budget:
                        rec.aug_budget = rec.aug_budget + data.aug_budget
                    if data.sep_budget:
                        rec.sep_budget = rec.sep_budget + data.sep_budget
                    if data.oct_budget:
                        rec.oct_budget = rec.oct_budget + data.oct_budget
                    if data.nov_budget:
                        rec.nov_budget = rec.nov_budget + data.nov_budget
                    if data.dec_budget:
                        rec.dec_budget = rec.dec_budget + data.dec_budget
                    if data.jan_budget:
                        rec.jan_budget = rec.jan_budget + data.jan_budget
                    if data.feb_budget:
                        rec.feb_budget = rec.feb_budget + data.feb_budget
                    if data.mar_budget:
                        rec.mar_budget = rec.mar_budget + data.mar_budget
                    if data.remark:
                        rec.remark = data.remark
                    if data.expense_type:
                        rec.expense_type = data.expense_type
                    rec.calulate_total_planed_amount()
                    data.unlink()
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False
                    rec.id_revise_bool = True
                    rec.id_new_line_bool = False
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Approved',
                        'approve_date': date.today(),
                        'total_amount': rec.total_amount,
                        'revise_budget_status': 'approved_by_approver',
                    })
                # elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                #     rec.revenue_budget_id.pending_at_ids = False
                #     rec.approver_approved_button_boolean = False
                #     rec.revised_button_hide_boolean = True
                #     data = self.env['revised_revenue_budget_wizard'].search([('revenue_expense_id', '=', rec.id)],limit=1)
                #     # print(data.expense_type, '=====================>>>>>>>>>>>')
                #     rec.expense_type = data.expense_type
                #     rec.remark = data.remarks
                #     rec.state = 'validate'
                #     month_mapping = {
                #         'April': 'apr_budget',
                #         'May': 'may_budget',
                #         'Jun': 'jun_budget',
                #         'July': 'jul_budget',
                #         'August': 'aug_budget',
                #         'September': 'sep_budget',
                #         'October': 'oct_budget',
                #         'November': 'nov_budget',
                #         'December': 'dec_budget',
                #         'January': 'jan_budget',
                #         'February': 'feb_budget',
                #         'March': 'mar_budget',
                #     }
                #     total_amountt = 0
                #     for recc in data.revised_amount_ids:
                #         total_amountt += recc.revised_amount
                #         month_field = month_mapping.get(recc.month_revies)
                #         if month_field:
                #             setattr(rec, month_field, getattr(rec, month_field) + recc.revised_amount)
                #     rec.total_amount += total_amountt
                #     data.revised_amount_ids.unlink()
                #     data.unlink()
                #     val = []
                #     for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                #         if dataa.state in ['re_f_approved', 'confirm']:
                #             val.append(dataa.state)
                #     if len(val) == 0:
                #         rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False
                #     log_data.write({
                #         'approve_by': self.env.user.employee_ids.name,
                #         'state': 'Approved',
                #         'approve_date': date.today(),
                #         'total_amount': rec.total_amount,
                #         'revise_budget_status': 'approved_by_approver',
                #     })
            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'validate'
                    rec.id_new_line_bool = True
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    rec.revenue_budget_id.add_expense_line_hide_boolean = True
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state in ['re_f_approved', 'confirm']:
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False  # for search method

                    approver_ids = False
                    l2_pending_line = self.env['kw_revenue_budget_line'].search(
                        [('revenue_budget_id', '=', self.revenue_budget_id.id),
                         ('l2_approve_button_boolean', '=', True),
                         ('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                    if l2_pending_line:
                        l2_approver_ids = self.revenue_budget_id.budget_department.level_2_approver.ids
                        # print(l2_approver_ids, 'apppppppppppp')
                        if l2_approver_ids:
                            approver_ids = l2_approver_ids
                    finance_pending = self.env['kw_revenue_budget_line'].search(
                        [('revenue_budget_id', '=', self.revenue_budget_id.id),
                         ('finance_approved_button_boolean', '=', True),
                         ('state', 'in', ('re_apply', 'to_approve')), ('id', '!=', self.id)])
                    if not finance_pending:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False
                    if finance_pending:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = True
                        finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
                        finance_group_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                        if finance_group_users:
                            finance_users = finance_group_users.mapped('employee_ids.id')
                            if approver_ids:
                                approver_ids = approver_ids + finance_users
                                approver_ids = list(dict.fromkeys(approver_ids))

                    rec.revenue_budget_id.pending_at_ids = approver_ids

                elif self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    if not rec.account_code_id:
                        raise ValidationError('Please set Account Code.')
                    approver_group = self.env.ref(
                        'kw_budget.group_approver_kw_budget')
                    approver_users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
                    if not approver_users:
                        raise ValidationError("No users found in the approver group.")
                    approver_ids = approver_users.mapped('employee_ids.id')

                    pending_finance_lines = self.env['kw_revenue_budget_line'].search(
                        [('revenue_budget_id', '=', rec.revenue_budget_id.id), ('state', '=', 'to_approve'),
                         ('id', '!=', self.id), ('l2_approve_button_boolean', '=', False),
                         ('finance_approved_button_boolean', '=', True)])
                    if not pending_finance_lines:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False
                    if pending_finance_lines:

                        finance_group = self.env.ref('kw_budget.group_finance_kw_budget')
                        finance_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
                        if finance_users:
                            finance_users_ids = approver_users.mapped('employee_ids.id')
                            approver_ids = approver_ids + finance_users_ids
                            approver_ids = list(dict.fromkeys(approver_ids))

                    rec.revenue_budget_id.pending_at_ids = [(6, 0, approver_ids)]
                    rec.state = 'confirm'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = True
                    rec.revenue_budget_id.revenue_revised_approver_approval_boolean = True  # for search method
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.finance_approved_button_boolean:
                            if dataa.state in ['to_approve', 're_apply']:
                                val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False  # for search method

    def revised_data_send_back(self):
        for rec in self:
            log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                [('revenue_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = False
                    rec.edit_button_hide_boolean = True
                    log_data.write({
                        'state': 'Sent Back',
                        'approve_date': date.today(),
                    })

    def reject_revised_revenue_budget(self):
        # log_record = self.env['kw_revise_revenue_budget_action_log'].search([('revenue_budget_line_id', '=', self.id),('approved','=',False)],limit=1)
        for rec in self:
            log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                [('revenue_budget_line_id', '=', rec.id),
                 ('name_of_expenses', '=', rec.name_of_expenses),
                 ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
            if rec.state in ['draft', 're_apply', 're_f_approved', 'validate']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.state = 'validate'
                    rec.approver_approved_button_boolean = False
                    rec.finance_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state == 're_apply':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False  # record for search view
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = True  # record for search view
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'revise_budget_status': 'rejected_by_finance',
                    })
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    data = self.env['revised_revenue_budget_wizard'].search([('revenue_expense_id', '=', rec.id)],
                                                                            limit=1)
                    rec.state = 'validate'
                    data.revised_amount_ids.unlink()
                    data.unlink()
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state == 're_f_approved':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False
                    log_data.write({
                        'approve_by': self.env.user.employee_ids.name,
                        'state': 'Rejected',
                        'approve_date': date.today(),
                        'total_amount': rec.total_amount,
                        'revise_budget_status': 'rejected_by_approver',
                    })
            elif rec.state in ['to_approve', 'confirm']:
                if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.state = 'cancel'
                    rec.finance_approved_button_boolean = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    rec.edit_button_hide_boolean = False
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state == 'to_approve':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_finance_approval_boolean = False  # for search method
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False  # for search method
                        rec.revenue_budget_id.add_expense_line_hide_boolean = True
                elif self.env.user.has_group('kw_budget.group_approver_kw_budget'):
                    rec.state = 'cancel'
                    rec.revenue_budget_id.pending_at_ids = False
                    rec.approver_approved_button_boolean = False
                    rec.revised_button_hide_boolean = True
                    val = []
                    for dataa in rec.revenue_budget_id.revenue_budget_line_ids:
                        if dataa.state == 'confirm':
                            val.append(dataa.state)
                    if len(val) == 0:
                        rec.revenue_budget_id.revenue_revised_approver_approval_boolean = False  # for search method
                        rec.revenue_budget_id.add_expense_line_hide_boolean = True

    def edit_budget_button(self):
        for rec in self:
            data = self.env['revised_revenue_budget_wizard'].sudo().search([('revenue_expense_id', '=', rec.id)],
                                                                           limit=1)
            default_revised_amount_ids = [
                {'month_revies': item.month_revies, 'revised_amount': item.revised_amount}
                for item in data.revised_amount_ids
            ]
            return {
                'name': 'Revised Revenue Budget Wizard',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'revised_revenue_budget_wizard',
                'view_id': self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_revenue_expense_id': rec.id,
                    'default_name_of_expenses': rec.name_of_expenses,
                    'default_expense_type': rec.expense_type,
                    'default_revised_amount_ids': default_revised_amount_ids,
                },
            }


class RevenueBudgetLinewizard(models.Model):
    _name = 'kw_revenue_budget_line_wizard'
    _rec_name = 'name_of_expenses'

    name_of_expenses = fields.Char('Name of expenses', required=True)
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
    revise_amount = fields.Float('Revise Amount')
    spent_amount = fields.Float('Spent Amount')
    total_amount = fields.Float('Total Amount')
    remark = fields.Text('Remark')
    wizard_id = fields.Many2one('revised_revenue_budget_wizard', 'Revenue Budget')
    expense_type = fields.Selection(string='Head of Expenses',
                                    selection=[('Income', 'Income'), ('Expenses', 'Expenses')])
    finance_approved_button_boolean = fields.Boolean()
    approver_approved_button_boolean = fields.Boolean()
    approver_reverted_button_boolean = fields.Boolean()
    revised_button_hide_boolean = fields.Boolean()
    edit_button_hide_boolean = fields.Boolean()
    budgetary_position_id = fields.Many2one('account.budget.post')
    l2_approve_button_boolean = fields.Boolean()
    # actual_amount = fields.Float('Actual Amount', compute="_compute_practical_amount", readonly=True)
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


class RevisedRevenueWizard(models.Model):
    _name = 'revised_revenue_budget_wizard'
    _description = 'revised button wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'revenue_budget_id'

    def _get_budget_lines(self):
        domain = [('id', '=', 0)]
        budget_id = self.env.context.get('default_revenue_id')
        if budget_id:
            budget_line_ids = self.env['kw_revenue_budget_line'].search([('revenue_budget_id', '=', budget_id)])
            new_lines = []
            if budget_line_ids:
                budet_lines_ids = [line.id for line in budget_line_ids]
                domain = [('id', 'in', budet_lines_ids)]
        return domain

    revised_amount = fields.Float(string='Revise Amount')
    remarks = fields.Text(string='Remarks')
    month_revies = fields.Selection(string="Month of Revies",
                                    selection=[('April', 'Apr'), ('May', 'May'), ('Jun', 'Jun'),
                                               ('July', 'July'), ('August', 'Aug'),
                                               ('September', 'Sep'), ('October', 'Oct'),
                                               ('November', 'Nov'), ('December', 'Dec'), ('January', 'Jan'),
                                               ('February', 'Feb'), ('March', 'Mar')])
    revenue_expense_id = fields.Many2one('kw_revenue_budget_line', domain=_get_budget_lines)
    revenue_budget_id = fields.Many2one('kw_revenue_budget', string="Budget",
                                        default=lambda self: self.env['kw_revenue_budget'].sudo().search(
                                            [('id', '=', self.env.context.get('active_id'))]))
    revised_amount_ids = fields.One2many('revised_revenue_budget_data', 'wizard_id', string='Revised Amounts')
    name_of_expenses = fields.Char('Name of expenses')
    expense_type = fields.Selection(string='Expenses Type', selection=[('Income', 'Income'), ('Expenses', 'Expenses')])
    for_new_line = fields.Boolean('For New Budget Line')
    for_revise_line = fields.Boolean('For Revise Budget Line')
    revenue_budget_line_ids = fields.One2many('kw_revenue_budget_line', 'revenue_budget_revise', 'Revenue Budget Lines',
                                              copy=True)
    existing_revenue_budget_line_ids = fields.One2many('kw_revenue_budget_line_wizard', 'wizard_id',
                                                       'Revenue Budget Lines')
    pending_at = fields.Selection(string="Pending At",
                                  selection=[('L1', 'L1'), ('L2', 'L2'), ('Finance', 'Finance'),
                                             ('cfo', 'Finance(CFO)'), ('Approver', 'Approver'),
                                             ('Validate', 'Validate'), ('Cancel', 'Cancel')], default="L1",
                                  track_visibility='onchange')

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

    def get_boolean_all(self):
        for rec in self:
            rec.show_apply = True if rec.pending_at == 'L1' and self.env.user.employee_ids.id in rec.revenue_budget_id.budget_department.level_1_approver.ids else False

    # @api.onchange('revenue_budget_id')
    def onchnage_budget_details(self):
        if self.revenue_budget_id:
            self.budget_department = self.revenue_budget_id.budget_department.name
            self.branch_id = self.revenue_budget_id.branch_id.name

    @api.onchange('for_new_line', 'for_revise_line')
    def onchnage_budget_details_data(self):
        if not self.for_new_line:
            self.revenue_budget_line_ids.unlink()
        if not self.for_revise_line:
            self.revised_amount_ids.unlink()
            self.existing_revenue_budget_line_ids.unlink()

    @api.onchange('revised_amount_ids')
    def _onchange_existing_lines(self):
        if self.revised_amount_ids:
            new_lines = []
            self.existing_revenue_budget_line_ids = [(5, 0, 0)]
            for rec in self.revised_amount_ids:
                if rec.expense_id:
                    new_lines.append((0, 0, {
                        "name_of_expenses": rec.expense_id.name_of_expenses,
                        "sequence_ref": rec.expense_id.sequence_ref,
                        "expense_type": rec.expense_id.expense_type,
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
                        "total_amount": rec.expense_id.total_amount,
                        "wizard_id": self.id,
                        "remark": rec.expense_id.remark,

                    }))
            self.existing_revenue_budget_line_ids = new_lines

    def format_revised_amounts(self, line_obj):
        format_rev_amts = []
        formatted_amount = ''
        for rec in line_obj:
            if rec.apr_budget:
                formatted_amount += f"{'April'} : {rec.apr_budget}"
            if rec.may_budget:
                formatted_amount += f"{'May'} : {rec.may_budget}"
            if rec.jun_budget:
                formatted_amount += f"{'June'} : {rec.jun_budget}"
            if rec.jul_budget:
                formatted_amount += f"{'July'} : {rec.jul_budget}"
            if rec.aug_budget:
                formatted_amount += f"{'August'} : {rec.aug_budget}"
            if rec.sep_budget:
                formatted_amount += f"{'September'} : {rec.sep_budget}"
            if rec.oct_budget:
                formatted_amount += f"{'October'} : {rec.oct_budget}"
            if rec.nov_budget:
                formatted_amount += f"{'November'} : {rec.nov_budget}"
            if rec.dec_budget:
                formatted_amount += f"{'December'} : {rec.dec_budget}"
            if rec.jan_budget:
                formatted_amount += f"{'January'} : {rec.jan_budget}"
            if rec.feb_budget:
                formatted_amount += f"{'April'} : {rec.feb_budget}"
            if rec.mar_budget:
                formatted_amount += f"{'March'} : {rec.mar_budget}"
            format_rev_amts.append(formatted_amount)
        return ', '.join(format_rev_amts)

    @api.multi
    def open_take_action_budget_lines(self):
        pass

    #     ''' function is used to redirect revise/ADD revenue Budget lines list, form view. '''
    #     res = self.env.ref('kw_budget.action_revised_revenue_budget_wizard').read()[0]
    #     l2_ids = []
    #     l1_ids = []
    #     l1_budget_obj = []
    #     l2_budget_obj = []
    #     res['context'] = {'create': False, 'edit': True}
    #     user = self.env.user.employee_ids
    #     budget_department_id = self.env['kw_budget_dept_mapping'].search([
    #         ('level_2_approver.id', '=', user.id)])
    #     if budget_department_id:
    #         if len(budget_department_id) == 1:
    #             query = "select id from kw_revenue_budget where budget_department = " + str(
    #                 budget_department_id.id)
    #         if len(budget_department_id) > 1:
    #             query = "select id from kw_revenue_budget where budget_department in " + str(
    #                 tuple(budget_department_id.ids))
    #         self._cr.execute(query)
    #         ids = self._cr.fetchall()
    #         if ids:
    #             l2_ids = [x[0] for x in ids]
    #             l2_budget_obj = self.env['revised_revenue_budget_wizard'].sudo().search([('revenue_budget_id', 'in', tuple(l2_ids)), ('pending_at', '=', 'L2')]).ids
    #             res['context'] = {'create': False, 'edit': True}
    #     budget_department_id_l1 = self.env['kw_budget_dept_mapping'].search([
    #         ('level_1_approver.id', '=', user.id)])
    #     if budget_department_id_l1:
    #         if len(budget_department_id_l1) == 1:
    #             l1query = "select id from kw_revenue_budget where budget_department = " + str(
    #                 budget_department_id_l1.id)
    #             print(l1query, '%%%%%%%%')
    #         if len(budget_department_id_l1) > 1:
    #             l1query = "select id from kw_revenue_budget where budget_department in " + str(
    #                 tuple(budget_department_id_l1.ids))
    #         self._cr.execute(l1query)
    #         l1_ids = self._cr.fetchall()
    #         print(l1_ids, 'oooo')
    #         if l1_ids:
    #             l1_ids = [x[0] for x in l1_ids]
    #             l1_budget_obj = self.env['revised_revenue_budget_wizard'].sudo().search(
    #                 [('revenue_budget_id', 'in', tuple(l1_ids))]).ids
    #             res['context'] = {'create': False, 'edit': True}
    #             print(l1_budget_obj, "*********", l1_budget_obj, ids)
    #
    #     if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
    #         finance_budget_obj = []
    #         budget_obj = self.env['revised_revenue_budget_wizard'].sudo().search(
    #             [('pending_at', '=', 'Approver')]).ids
    #         print(budget_obj, 'approver')
    #         if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #             finance_budget_obj = self.env['revised_revenue_budget_wizard'].sudo().search(
    #                 [('pending_at', '=', 'Finance')]).ids
    #
    #         budget_obj = budget_obj + finance_budget_obj + l1_budget_obj + l2_budget_obj
    #         print(budget_obj, l1_budget_obj, l2_budget_obj, finance_budget_obj, 'Approver after')
    #
    #         res['views'] = [(self.env.ref('kw_budget.view_revised_amount_revenue_wizard_tree').id, 'list'),
    #                         (self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id, 'form')]
    #         res['domain'] = [('id', 'in', budget_obj)]
    #
    #         return res
    #
    #
    #     if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
    #         budget_obj = self.env['revised_revenue_budget_wizard'].sudo().search(
    #             [('pending_at', '=', 'Finance')]).ids
    #         print(budget_obj, 'PPPPPPPPPPPPPPPPPPPPBB')
    #         budget_obj = budget_obj + l1_budget_obj + l2_budget_obj
    #         print(budget_obj, l1_budget_obj, l2_budget_obj, [('id', 'in', tuple(budget_obj))])
    #         res['views'] = [(self.env.ref('kw_budget.view_revised_amount_revenue_wizard_tree').id, 'list'),
    #                         (self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id, 'form')]
    #         res['domain'] = [('id', 'in', budget_obj)]
    #         print(res, 'Pccccccccccccccc')
    #         res['context'] = {'create': False, 'edit': True}
    #         return res
    #
    #     if self.env.user.has_group('kw_budget.group_l2_kw_budget'):
    #         domain_ids = []
    #         domain_ids = l2_budget_obj + l1_budget_obj
    #         print(domain_ids, 'pppppfffffffffff')
    #         res['views'] = [(self.env.ref('kw_budget.view_revised_amount_revenue_wizard_tree').id, 'list'),
    #                         (self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id, 'form')]
    #         res['domain'] = [('id', 'in', domain_ids)]
    #         res['context'] = {'create': False, 'edit': True}
    #         return res
    #
    #     else:
    #         domain_ids =  l1_budget_obj
    #         res['views'] = [(self.env.ref('kw_budget.view_revised_amount_revenue_wizard_tree').id, 'list'),
    #                         (self.env.ref('kw_budget.revised_amount_revenue_wizard_form').id, 'form')]
    #         res['domain'] = [('id', 'in', domain_ids)]
    #         res['context'] = {'create': False, 'edit': True}
    #         return res
    #
    #
    #
    #     return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        l2_ids = []
        l1_ids = []
        l1_budget_obj = []
        l2_budget_obj = []
        user = self.env.user.employee_ids
        budget_department_id = self.env['kw_budget_dept_mapping'].sudo().search([
            ('level_2_approver.id', '=', user.id)])
        if budget_department_id:
            if len(budget_department_id) == 1:
                query = "select id from kw_revenue_budget where budget_department = " + str(
                    budget_department_id.id)
            if len(budget_department_id) > 1:
                query = "select id from kw_revenue_budget where budget_department in " + str(
                    tuple(budget_department_id.ids))
            self._cr.execute(query)
            ids = self._cr.fetchall()
            if ids:
                l2_ids = [x[0] for x in ids]
                query = """
                        SELECT id
                        FROM revised_revenue_budget_wizard
                        WHERE revenue_budget_id IN %s
                        AND pending_at = 'L2'
                    """
                self._cr.execute(query, (tuple(l2_ids),))
                lines_obj = self._cr.fetchall()
                l2_budget_obj = [data[0] for data in lines_obj]
        budget_department_id_l1 = self.env['kw_budget_dept_mapping'].sudo().search([
            ('level_1_approver.id', '=', user.id)])
        if budget_department_id_l1:
            if len(budget_department_id_l1) == 1:
                l1query = "select id from kw_revenue_budget where budget_department = " + str(
                    budget_department_id_l1.id)
            if len(budget_department_id_l1) > 1:
                l1query = "select id from kw_revenue_budget where budget_department in " + str(
                    tuple(budget_department_id_l1.ids))
            self._cr.execute(l1query)
            l1_ids = self._cr.fetchall()
            if l1_ids:
                l1_ids = [x[0] for x in l1_ids]
                query = """
                        SELECT id
                        FROM revised_revenue_budget_wizard
                        WHERE revenue_budget_id IN %s
                    """
                self._cr.execute(query, (tuple(l1_ids),))
                lines_obj = self._cr.fetchall()
                l1_budget_obj = [data[0] for data in lines_obj]
        if self.env.user.has_group('kw_budget.group_manager_kw_budget'):
            query = """
                                SELECT id
                                FROM revised_revenue_budget_wizard
                            """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            # print(budget_obj, 'approver')

            budget_obj = budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_approver_kw_budget'):
            finance_budget_obj = []
            cfo_budget_obj = []
            query = """
                    SELECT id
                    FROM revised_revenue_budget_wizard
                    WHERE pending_at = 'Approver'
                """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            # print(budget_obj, 'approver')
            if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
                query = """
                            SELECT id
                            FROM revised_revenue_budget_wizard
                            WHERE pending_at = 'cfo'
                        """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                cfo_budget_obj = [data[0] for data in lines_obj]

            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                            SELECT id
                            FROM revised_revenue_budget_wizard
                            WHERE pending_at = 'Finance'
                        """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                finance_budget_obj = [data[0] for data in lines_obj]

            budget_obj = budget_obj + cfo_budget_obj + finance_budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', budget_obj)]
            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_cfo_kw_budget'):
            finance_budget_obj = []
            query = """
                                        SELECT id
                                        FROM revised_revenue_budget_wizard
                                        WHERE pending_at = 'cfo'
                                    """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            cfo_budget_obj = [data[0] for data in lines_obj]

            if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
                query = """
                            SELECT id
                            FROM revised_revenue_budget_wizard
                            WHERE pending_at = 'Finance'
                        """
                self._cr.execute(query)
                lines_obj = self._cr.fetchall()
                finance_budget_obj = [data[0] for data in lines_obj]

            cfo_budget_obj = cfo_budget_obj + finance_budget_obj + l1_budget_obj + l2_budget_obj
            args = [('id', 'in', cfo_budget_obj)]
            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)

        if self.env.user.has_group('kw_budget.group_finance_kw_budget'):
            query = """
                    SELECT id
                    FROM revised_revenue_budget_wizard
                    WHERE pending_at = 'Finance'
                """
            self._cr.execute(query)
            lines_obj = self._cr.fetchall()
            budget_obj = [data[0] for data in lines_obj]
            # print(budget_obj, 'PPPPPPPPPPPPPPPPPPPPBB')
            budget_obj = budget_obj + l1_budget_obj + l2_budget_obj
            print(budget_obj, l1_budget_obj, l2_budget_obj, [('id', 'in', tuple(budget_obj))])
            args = [('id', 'in', budget_obj)]
            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('kw_budget.group_l2_kw_budget'):
            domain_ids = []
            domain_ids = l2_budget_obj + l1_budget_obj
            # print(domain_ids, 'pppppfffffffffff')
            args = [('id', 'in', domain_ids)]

            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)
        else:
            domain_ids = l1_budget_obj
            args = [('id', 'in', domain_ids)]
            return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                             count=count, access_rights_uid=access_rights_uid)
        return super(RevisedRevenueWizard, self)._search(args, offset=offset, limit=limit, order=order,
                                                         count=count, access_rights_uid=access_rights_uid)

    @api.onchange('revenue_expense_id')
    def get_value(self):
        self.name_of_expenses = self.revenue_expense_id.name_of_expenses
        self.expense_type = self.revenue_expense_id.expense_type

    def revenue_revised_add_line_submit(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_revenue_budget'].sudo().search([('id', '=', active_ids)])
        for rec in self.revenue_budget_line_ids:
            rec.revenue_budget_id = data.id
            rec.state = 'to_approve'
            rec.edit_button_hide_boolean = True
            rec.l2_approve_button_boolean = True
            data.revenue_revised_finance_approval_boolean = False
            rec.finance_approved_button_boolean = False
            rec.revised_button_hide_boolean = False
            data.add_expense_line_hide_boolean = False
            approver_ids = data.budget_department.level_2_approver.ids
            data.write({'pending_at_ids': [(6, 0, approver_ids)]

                        })
        # self.unlink()

    # def revenue_revised_amount_submit(self):
    #     print(self.env.context.get('default_revenue_id'), '************xxxx**********')
    #     # flag= False
    #     if self.for_revise_line:
    #         # data = self.env['revised_revenue_budget_wizard'].sudo().search([('revenue_expense_id', '=', self.env.context.get('default_revenue_id'))]) - self
    #         # data.unlink()
    #         print(self.revised_amount_ids, 'RRRRRRRRRRRRRRRRRR')
    #         for rec in self.revised_amount_ids:
    #             rec.expense_id.revenue_budget_id.revenue_revised_finance_approval_boolean = False
    #             rec.expense_id.l2_approve_button_boolean = True
    #             rec.expense_id.finance_approved_button_boolean = False
    #             rec.expense_id.revised_button_hide_boolean = False
    #             rec.expense_id.edit_button_hide_boolean = True
    #             rec.expense_id.state = 're_apply'
    #             rec.expense_id.id_revise_bool = False
    #             rec.expense_id.id_new_line_bool = False
    #             # rec.revenue_expense_id.revenue_budget_id.revised_amount = self.revised_amount
    #             # rec.revenue_expense_id.revenue_budget_id.revised_month = self.month_revies
    #             # finance_group = self.env.ref(
    #             #     'kw_budget.group_finance_kw_budget')
    #             # finance_group_users = self.env['res.users'].search([('groups_id', 'in', finance_group.id)])
    #             # if not finance_group_users:
    #             #     raise ValidationError("No users found in the finance group.")
    #             # finance_ids = finance_group_users.mapped('employee_ids.id')
    #
    #             format_rev_amts = self.format_revised_amounts()
    #             log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
    #                 [('revenue_budget_line_id', '=', rec.expense_id.id),
    #                  ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
    #                  ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
    #             if log_data:
    #                 log_data.write({
    #                     'name_of_expenses': rec.revenue_expense_id.name_of_expenses,
    #                     'revised_amount': format_rev_amts,
    #                     'total_amount': rec.revenue_expense_id.total_amount,
    #                     'approver_by': self.env.user.employee_ids.name,
    #                     'revenue_budget_line_id': rec.revenue_expense_id.id,
    #                     'state': 'Applied',
    #                     'revise_budget_status': 'applied',
    #                 })
    #                 rec.revenue_expense_id.revenue_budget_id.write({
    #                     'pending_at_ids': [
    #                         (6, 0, rec.revenue_expense_id.revenue_budget_id.budget_department.level_2_approver.ids)]
    #                 })
    #             else:
    #                 rec.expense_id.revenue_budget_id.write({
    #                     'revise_revenue_action_log_ids': [[0, 0, {
    #                         'name_of_expenses': rec.expense_id.name_of_expenses,
    #                         'revised_amount': format_rev_amts,
    #                         'total_amount': rec.expense_id.total_amount,
    #                         'approver_by': self.env.user.employee_ids.name,
    #                         'revenue_budget_line_id': rec.expense_id.id,
    #                         'state': 'Applied',
    #                         'revise_budget_status': 'applied',
    #                     }]],
    #                     'pending_at_ids': [
    #                         (6, 0, rec.expense_id.revenue_budget_id.budget_department.level_2_approver.ids)]
    #                 })
    #
    #     if self.for_new_line:
    #         self.revenue_revised_add_line_submit()
    #         if not self.for_revise_line:
    #             self.revenue_revised_add_line_submit()

    def revenue_revised_amount_submit(self):
        if self.pending_at == 'L1':
            self.pending_at = 'L2'
        elif self.pending_at == 'L2':
            self.pending_at = 'Finance'
        elif self.pending_at == 'Finance':
            self.pending_at = 'Approver'
        elif self.pending_at == 'Approver':
            self.pending_at = ""
            if self.revenue_budget_line_ids:
                cline_changes = self.format_revised_amounts()
                for line in self.revenue_budget_line_ids:
                    line.revenue_budget_id = self.revenue_budget_id

    def confirm_apply(self):
        count = 0
        if len(self.revised_amount_ids) > 0:
            count += len(self.revised_amount_ids)
        if len(self.revenue_budget_line_ids) > 0:
            count += len(self.revenue_budget_line_ids)
        if count == 0:
            raise ValidationError("Please add atleast one line.")
        self.onchnage_budget_details()
        if self.pending_at == 'L1':
            self.pending_at = 'L2'
        if self.revised_amount_ids and self.for_revise_line:

            for rec in self.revised_amount_ids:
                line_changes = self.format_revised_amounts(rec)
                log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                    [('revenue_budget_line_id', '=', rec.expense_id.id),
                     ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                     ('revise_budget_status', 'in', ['applied', 'approved_by_finance'])])
                if log_data:
                    log_data.write({
                        'name_of_expenses': rec.expense_id.name_of_expenses,
                        'revised_amount': line_changes,
                        'total_amount': rec.expense_id.total_amount,
                        'revise_amount': rec.revised_amount,
                        'total': rec.expense_id.total_amount + rec.revised_amount,
                        'approver_by': self.env.user.employee_ids.name,
                        'revenue_budget_line_id': rec.expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    })
                if not log_data:
                    self.env['kw_revise_revenue_budget_action_log'].sudo().create({
                        'name_of_expenses': rec.expense_id.name_of_expenses,
                        'revised_amount': line_changes,
                        'total_amount': rec.expense_id.total_amount,
                        'revise_amount': rec.revised_amount,
                        'total': rec.expense_id.total_amount + rec.revised_amount,
                        'approver_by': self.env.user.employee_ids.name,
                        'revenue_budget_line_id': rec.expense_id.id,
                        'state': 'Applied',
                        'revise_budget_status': 'applied',
                    })

    def confirm_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Finance'
            if self.revised_amount_ids and self.for_revise_line:

                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                        [('revenue_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in', ['applied'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': line_changes,
                            'total_amount': rec.expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'revenue_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By L2',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_l2',
                        })

    def cancel_l2(self):
        if self.pending_at == 'L2':
            self.pending_at = 'Cancel'

    def confirm_finance(self):
        if self.pending_at == 'Finance':
            for lines in self.revenue_budget_line_ids:
                if not lines.account_code_id:
                    raise ValidationError(f'Account Code is  not set for the expense {lines.name_of_expenses}')
            self.pending_at = 'cfo'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                        [('revenue_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in', ['applied', 'approved_by_l2', 'approved_by_finance'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': line_changes,
                            'total_amount': rec.expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'revenue_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By Finance',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_finance',
                        })

    def Cancel_finance(self):
        if self.pending_at == 'Finance':
            self.pending_at = 'Cancel'

    def confirm_cfo(self):
        if self.pending_at == 'cfo':
            # for lines in self.revenue_budget_line_ids:
            #     if not lines.account_code_id:
            #         raise ValidationError(f'Account Code is  not set for the expense {lines.name_of_expenses}')
            self.pending_at = 'Approver'
            if self.revised_amount_ids and self.for_revise_line:
                for rec in self.revised_amount_ids:
                    line_changes = self.format_revised_amounts(rec)
                    log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                        [('revenue_budget_line_id', '=', rec.expense_id.id),
                         ('name_of_expenses', '=', rec.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in',
                          ['applied', 'approved_by_l2', 'approved_by_finance', 'approved_by_cfo'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': rec.expense_id.name_of_expenses,
                            'revised_amount': line_changes,
                            'total_amount': rec.expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'revenue_budget_line_id': rec.expense_id.id,
                            'state': 'Approved By Finance(CFO)',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_cfo',
                        })

    def Cancel_cfo(self):
        if self.pending_at == 'cfo':
            self.pending_at = 'Cancel'

    def confirm_approver(self):
        if self.pending_at == 'Approver':
            self.pending_at = 'Validate'
            if self.revenue_budget_line_ids and self.for_new_line:
                for line in self.revenue_budget_line_ids:
                    line.revenue_budget_id = self.revenue_budget_id
                    line.state = 'validate'
                    line.id_new_line_bool = True
            if self.revised_amount_ids and self.for_revise_line:

                for data in self.revised_amount_ids:

                    line_changes = self.format_revised_amounts(data)
                    log_data = self.env['kw_revise_revenue_budget_action_log'].sudo().search(
                        [('revenue_budget_line_id', '=', data.expense_id.id),
                         ('name_of_expenses', '=', data.expense_id.name_of_expenses),
                         ('revise_budget_status', 'in',
                          ['applied', 'L2 Approved', 'approved_by_finance', 'approved_by_cfo'])])
                    if log_data:
                        log_data.write({
                            'name_of_expenses': data.expense_id.name_of_expenses,
                            'revised_amount': line_changes,
                            'total_amount': data.expense_id.total_amount,
                            'approve_by': self.env.user.employee_ids.name,
                            'approve_by': self.env.user.employee_ids.name,
                            'revenue_budget_line_id': data.expense_id.id,
                            'state': 'Approved',
                            'approve_date': date.today(),
                            'revise_budget_status': 'approved_by_approver',
                        })
                    if data.apr_budget:
                        data.expense_id.apr_budget = data.expense_id.apr_budget + data.apr_budget
                    if data.may_budget:
                        data.expense_id.may_budget = data.expense_id.may_budget + data.may_budget
                    if data.jun_budget:
                        data.expense_id.jun_budget = data.expense_id.jun_budget + data.jun_budget
                    if data.jul_budget:
                        data.expense_id.jul_budget = data.expense_id.jul_budget + data.jul_budget
                    if data.aug_budget:
                        data.expense_id.aug_budget = data.expense_id.aug_budget + data.aug_budget
                    if data.sep_budget:
                        data.expense_id.sep_budget = data.expense_id.sep_budget + data.sep_budget
                    if data.oct_budget:
                        data.expense_id.oct_budget = data.expense_id.oct_budget + data.oct_budget
                    if data.nov_budget:
                        data.expense_id.nov_budget = data.expense_id.nov_budget + data.nov_budget
                    if data.dec_budget:
                        data.expense_id.dec_budget = data.expense_id.dec_budget + data.dec_budget
                    if data.jan_budget:
                        data.expense_id.jan_budget = data.expense_id.jan_budget + data.jan_budget
                    if data.feb_budget:
                        data.expense_id.feb_budget = data.expense_id.feb_budget + data.feb_budget
                    if data.mar_budget:
                        data.expense_id.mar_budget = data.expense_id.mar_budget + data.mar_budget
                    if data.remark:
                        data.expense_id.remark = data.remark
                    if data.expense_type:
                        data.expense_id.expense_type = data.expense_type
                    data.expense_id.state = 'validate'
                    data.expense_id.id_revise_bool = True

                    data.expense_id.calulate_total_planed_amount()

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

    def apply_l1(self):
        if self.pending_at == 'L1':
            self.pending_at = 'L2'


class RevisedAmount(models.Model):
    _name = 'revised_revenue_budget_data'
    _description = 'revised_revenue_budget'

    # def _get_budget_lines(self):
    #     if self.domain_char:
    #         print(self.domain_char, '*************')
    #         return ast.literal_eval(self.domain_char)

    month_revies = fields.Selection(string="Month of Revies",
                                    selection=[('April', 'Apr'), ('May', 'May'), ('Jun', 'Jun'),
                                               ('July', 'July'), ('August', 'Aug'),
                                               ('September', 'Sep'), ('October', 'Oct'),
                                               ('November', 'Nov'), ('December', 'Dec'), ('January', 'Jan'),
                                               ('February', 'Feb'), ('March', 'Mar')])
    add_sub_val = fields.Selection(string="Addition/Subtraction",
                                   selection=[
                                       ('add', 'Addition'), ('sub', 'Subtraction')])
    revised_amount = fields.Float(string='Revise Amount')
    wizard_id = fields.Many2one('revised_revenue_budget_wizard', string='Wizard')
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
    expense_id = fields.Many2one('kw_revenue_budget_line', 'Name of Expences')
    expense_type = fields.Char("Head of Expense")
    remark = fields.Char('Remarks')
    sequence_ref = fields.Char(string='Parent ID')

    @api.onchange('apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                  'aug_budget', 'sep_budget', 'oct_budget', 'nov_budget',
                  'dec_budget', 'jan_budget', 'feb_budget', 'mar_budget')
    def calulate_total_planed_amount(self):
        if not self._context.get('non_treasury_budget'):
            # for rec in self:
            self.revised_amount = False
            self.revised_amount = self.apr_budget + self.may_budget + self.jun_budget + \
                                  self.jul_budget + self.aug_budget + self.sep_budget + \
                                  self.oct_budget + self.nov_budget + self.dec_budget + \
                                  self.jan_budget + self.feb_budget + self.mar_budget

    @api.onchange('expense_id')
    def onchnage_head_of_expense(self):
        if self.expense_id:
            self.expense_type = self.expense_id.expense_type
            self.remark = self.expense_id.remark
            self.sequence_ref = self.expense_id.sequence_ref

    # @api.onchange('add_sub_val', 'revised_amount')
    # def _onchange_float_value(self):
    #     if self.add_sub_val:
    #         if self.add_sub_val == 'add':
    #             self.revised_amount = abs(self.revised_amount)
    #         if self.add_sub_val == 'sub':
    #             self.revised_amount = -abs(self.revised_amount)


class splltTreasurywizard(models.TransientModel):
    _name = "split_treasury_budget_wizard"

    def _get_budget_line_data(self):
        rec = self.env['kw_revenue_budget_line'].browse(self.env.context.get('active_ids'))
        return rec

    revenue_budget_id = fields.Many2one('kw_revenue_budget_line', 'Revenue Budget', default=_get_budget_line_data)
    budget_line_ids = fields.One2many('split_treasury_budget_wizard_line', 'wiz_id')
    name_of_expenses = fields.Char('Name of expenses', related='revenue_budget_id.name_of_expenses')
    apr_budget = fields.Float(related='revenue_budget_id.apr_budget')
    may_budget = fields.Float(related='revenue_budget_id.may_budget')
    jun_budget = fields.Float(related='revenue_budget_id.jun_budget')
    jul_budget = fields.Float(related='revenue_budget_id.jul_budget')
    aug_budget = fields.Float(related='revenue_budget_id.aug_budget')
    sep_budget = fields.Float(related='revenue_budget_id.sep_budget')
    oct_budget = fields.Float(related='revenue_budget_id.oct_budget')
    nov_budget = fields.Float(related='revenue_budget_id.nov_budget')
    dec_budget = fields.Float(related='revenue_budget_id.dec_budget')
    jan_budget = fields.Float(related='revenue_budget_id.jan_budget')
    feb_budget = fields.Float(related='revenue_budget_id.feb_budget')
    mar_budget = fields.Float(related='revenue_budget_id.mar_budget')
    total_amount = fields.Float(related='revenue_budget_id.total_amount')
    account_code_id = fields.Many2one('account.account', 'Account code', related='revenue_budget_id.account_code_id')
    remark = fields.Text(related='revenue_budget_id.remark')
    expense_type = fields.Selection(string='Head of Expenses', related='revenue_budget_id.expense_type')

    def split_treasury_budget(self):
        active_ids = self.env.context.get('active_id')
        data = self.env['kw_revenue_budget_line'].sudo().search([('id', '=', active_ids)])
        treasury_budget_line = self.env['kw_revenue_budget_line'].sudo().browse(active_ids)
        total_amount = treasury_budget_line.total_amount
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
            if treasury_budget_line.sequence_ref and str(treasury_budget_line.sequence_ref).isdigit():
                dataa = self.env['kw_revenue_budget_line'].sudo().search(
                    [('revenue_budget_id', '=', treasury_budget_line.revenue_budget_id.id)])
                alp = []
                for recc in dataa:
                    # if recc.state == 'validate':
                    import re
                    pattern = r'\d+'
                    numbers = re.findall(pattern, recc.sequence_ref)
                    int_numbers = [int(num) for num in numbers]
                    if int_numbers:
                        if not str(recc.sequence_ref).isdigit() and str(
                                int_numbers[0]) == treasury_budget_line.sequence_ref:
                            alp.append(recc.sequence_ref[-1])
                if len(alp) > 0:
                    numeric_part = treasury_budget_line.sequence_ref
                    sorted_alp = sorted(alp)
                    alpha = sorted_alp[-1]
                    next_alpha = chr(ord(alpha) + 1)
                    new_value = f"{numeric_part}{next_alpha}"
                else:
                    numeric_part = treasury_budget_line.sequence_ref
                    alpha_part = ''
                    next_alpha = 'A'
                    new_value = f"{numeric_part}{next_alpha}"

            new_budget_line = self.env['kw_revenue_budget_line'].sudo().create(
                {'name_of_expenses': rec.name_of_expenses,
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
                 'total_amount': rec.total_amount,
                 'expense_type': rec.expense_type,
                 'remark': rec.remark,
                 'revenue_budget_id': data.revenue_budget_id.id,
                 'state': 'validate',
                 'sequence_ref': new_value,
                 'hide_split_button_boolean': True,
                 'revised_button_hide_boolean': True
                 })
        data.write({
            month: treasury_budget_line[month] - new_monthly_amounts[month]
            for month in month_budget_sums
        })
        data.write({'total_amount': total_amount - sum(new_monthly_amounts.values())})


class SplitTreasuryWizardline(models.TransientModel):
    _name = 'split_treasury_budget_wizard_line'
    _description = 'Split Button Wizard'

    wiz_id = fields.Many2one('split_treasury_budget_wizard')
    name_of_expenses = fields.Char('Name of expenses', required=True)
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
    expense_type = fields.Selection(string='Head of Expenses',
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