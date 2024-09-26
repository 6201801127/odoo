import calendar
from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import date


def get_years():
    year_list = []
    # start_year = (date.today().year - (date.today().year - 2000))
    for i in range((date.today().year), 1998, -1):
        year_list.append((i, str(i)))
    return year_list


class kw_adv_salary_advance_report_wizard(models.TransientModel):
    _name = 'kw_advance_salary_advance_report_wizard'
    _description = 'Kw Salary advance Report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the salary advance at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the salary advance at that date")
    applied_by = fields.Selection([
        ('all', 'All'),
        ('dt', 'Date wise'),
        ('my', 'Month & Year wise'),
        ('employee', 'Employee'),
    ], string="Applied By", default='all')
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    year = fields.Selection(get_years(), string='Year')
    employee_ids = fields.Many2many('hr.employee', 'kw_advance_salary_advance_wiz_hr_employee_rel', 'advance_wiz_id',
                                    'employee_id', string="Employee")

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        employee_data = False
        if self.applied_by == 'employee':
            if self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group(
                    'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.employee_ids.department_id.manager_id.user_id.id == self.env.user.employee_ids.user_id.id:
                domain = ['|', '|', ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('id', '=', self.env.user.employee_ids.id)]
                employee_data = self.env['hr.employee'].sudo().search(domain)
            else:
                employee_data = self.env['hr.employee'].sudo().search([])
            return {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}

    def search_salary_advance_report(self):
        self.ensure_one()
        record_data = self.env['kw_advance_apply_salary_advance'].sudo().search([])
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_report_form').id

                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'view_mode': 'tree,form',
                        'view_type': 'form',
                        'name': 'Salary Advance Report',
                        'res_model': 'kw_advance_apply_salary_advance',
                        'domain': ['|',
                                   '&', ('create_date', '>=',  dt1), ('create_date', '<=',  dt2),
                                   '&',('payment_date', '>=', dt1), ('payment_date', '<=', dt2)],
                        'target': 'main',
                    }
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'view_mode': 'tree,form',
                        'view_type': 'form',
                        'name': 'Salary Advance Report',
                        'res_model': 'kw_advance_apply_salary_advance',
                        'domain': ['&',
                                   '|', ('create_date', '>=', dt1), ('create_date', '<=', dt2),
                                   '|', ('employee_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|', ('employee_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                    }
        elif self.applied_by == 'my':
            _, num_days = calendar.monthrange(self.year, int(self.month))
            first_day = datetime.date(self.year, int(self.month), 1)
            last_day = datetime.date(self.year, int(self.month), num_days)
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_report_form').id

                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'view_mode': 'tree,form',
                        'view_type': 'form',
                        'name': 'Salary Advance Report',
                        'res_model': 'kw_advance_apply_salary_advance',
                        'domain': ['|',
                                   '&', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                   '&',('payment_date', '>=', first_day), ('payment_date', '<=', last_day)],
                        'target': 'main',
                    }
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'view_mode': 'tree,form',
                        'view_type': 'form',
                        'name': 'Salary Advance Report',
                        'res_model': 'kw_advance_apply_salary_advance',
                        'domain': ['&',
                                   '|', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                   '|', ('employee_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|', ('employee_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                    }
        elif self.applied_by == 'employee':
            emp_id = self.employee_ids
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_report_form').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'name': 'Salary Advance Report',
                    'res_model': 'kw_advance_apply_salary_advance',
                    'domain': [('employee_id', 'in', emp_id.ids)],
                    'target': 'main',
                }
        elif self.applied_by == 'all':
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_report_form').id
                action = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'name': 'Salary Advance Report',
                    'res_model': 'kw_advance_apply_salary_advance',
                    'target': 'main',
                }
                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    action['domain'] = []
                else:
                    action['domain'] = ['|',('employee_id', '=', self.env.user.employee_ids.id),('employee_id.parent_id', '=', self.env.user.employee_ids.id)]
                return action


    @api.onchange('applied_by')
    def onchange_employee_id(self):
        if self.applied_by == 'employee' and self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_user') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_admin') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group(
                'kw_employee.group_hr_ra'):
            raise ValidationError("You are not eligible for this Option")


class kw_adv_petty_cash_report_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_report_wizard'
    _description = 'Petty cash Report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the petty cash at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the Petty cash at that date")
    applied_by = fields.Selection([
        ('all', 'All'),
        ('dt', 'Date wise'),
        ('my', 'Month & Year wise'),
        ('employee', 'Employee'),
    ], string="Applied By", default='all')
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    year = fields.Selection(get_years(), string='Year')
    employee_ids = fields.Many2many('hr.employee', 'kw_advance_petty_cash_wiz_hr_employee_rel', 'advance_wiz_id',
                                    'employee_id', string="Employee")

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        if self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group(
                    'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.employee_ids.department_id.manager_id.user_id.id == self.env.user.employee_ids.user_id.id:
            domain = ['|', '|', ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('id', '=', self.env.user.employee_ids.id)]
            employee_data = self.env['hr.employee'].sudo().search(domain)
        else:
            employee_data = self.env['hr.employee'].sudo().search([])
        return {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}


    def search_petty_cash_report(self):
        self.ensure_one()
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            record_data = self.env['kw_advance_apply_petty_cash'].sudo().search(
                ['|', 
                '&', ('create_date', '>=', dt1), ('create_date', '<=', dt2), 
                '&',('payment_date', '>=', dt1),('payment_date', '<=', dt2)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_petty_cash_tree_report').id

                if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree')],
                        'view_mode': 'tree,form',
                        'name': 'Petty Cash Report',
                        'res_model': 'kw_advance_apply_petty_cash',
                        'domain': ['|',
                                   '&', ('create_date', '>=', dt1), ('create_date', '<=', dt2),
                                   '&',('payment_date', '>=', dt1), ('payment_date', '<=', dt2)],
                        'target': 'main',
                    }
                # 'domain': [('create_date', '>=', dt1), ('create_date', '<=', dt2)],
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree')],
                        'view_mode': 'tree,form',
                        'name': 'Petty Cash Report',
                        'res_model': 'kw_advance_apply_petty_cash',
                        'domain': ['&',
                                   '|', ('create_date', '>=', dt1), ('create_date', '<=', dt2),
                                   '|', ('user_emp_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|', ('user_emp_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                    }
        elif self.applied_by == 'my':
            _, num_days = calendar.monthrange(self.year, int(self.month))
            first_day = datetime.date(self.year, int(self.month), 1)
            last_day = datetime.date(self.year, int(self.month), num_days)
            record_data = self.env['kw_advance_apply_petty_cash'].sudo().search(
                ['|', 
                '&', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                '&',('payment_date', '>=', first_day), ('payment_date', '<=', last_day)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_petty_cash_tree_report').id

                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree')],
                        'view_mode': 'tree,form',
                        'name': 'Petty Cash Report',
                        'res_model': 'kw_advance_apply_petty_cash',
                        'domain': ['|', 
                                   '&', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                   '&',('payment_date', '>=', first_day), ('payment_date', '<=', last_day)],
                        'target': 'main',
                    }
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree')],
                        'view_mode': 'tree,form',
                        'name': 'Petty Cash Report',
                        'res_model': 'kw_advance_apply_petty_cash',
                        'domain': ['&',
                                   '|', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                   '|', ('user_emp_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|', ('user_emp_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                    }
        elif self.applied_by == 'employee':
            emp_id = self.employee_ids
            record_data = self.env['kw_advance_apply_petty_cash'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_petty_cash_tree_report').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'name': 'Petty Cash Report',
                    'res_model': 'kw_advance_apply_petty_cash',
                    'domain': [('user_emp_id', 'in', emp_id.ids)],
                    'target': 'main',
                }
        
        elif self.applied_by == 'all':
            record_data = self.env['kw_advance_apply_petty_cash'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_apply_petty_cash_tree_report').id
                action = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'name': 'Petty Cash Report',
                    'res_model': 'kw_advance_apply_petty_cash',
                    'target': 'main',
                }
                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    action['domain'] = []
                else:
                    action['domain'] = ['|',('user_emp_id', '=', self.env.user.employee_ids.id),('user_emp_id.parent_id', '=', self.env.user.employee_ids.id)]
                return action

    @api.onchange('applied_by')
    def onchange_employee_id(self):
        if self.applied_by == 'employee' and self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_user') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_admin') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group(
                'kw_employee.group_hr_ra'):
            raise ValidationError("You are not eligible for this Option")


class kw_adv_claim_settlement_report_wizard(models.TransientModel):
    _name = 'kw_advance_claim_settlement_report_wizard'
    _description = 'Petty Cash Settelment Report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the Claim Settlement at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the Claim Settlement at that date")
    applied_by = fields.Selection([
        ('all','All'),
        ('dt', 'Date wise'),
        ('my', 'Month & Year wise'),
        ('employee', 'Employee'),
    ], string="Applied By", default='all')
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    year = fields.Selection(get_years(), string='Year')
    employee_ids = fields.Many2many('hr.employee', 'kw_advance_claim_settlement_wiz_hr_employee_rel', 'claim_wiz_id',
                                    'employee_id', string="Employee")

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        if self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group(
                    'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.employee_ids.department_id.manager_id.user_id.id == self.env.user.employee_ids.user_id.id:
            domain = ['|', '|', ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('id', '=', self.env.user.employee_ids.id)]
            employee_data = self.env['hr.employee'].sudo().search(domain)
        else:
            employee_data = self.env['hr.employee'].sudo().search([])
        return {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}

    def search_Claim_settlement_report(self):
        self.ensure_one()
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            record_data = self.env['kw_advance_claim_settlement'].sudo().search(
                ['|', 
                '&', ('create_date', '>=', dt1), ('create_date', '<=', dt2), 
                '&', ('payment_date', '>=', dt1),
                 ('payment_date', '<=', dt2)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_claim_settlement_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_report_form').id

                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form,tree',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'name': 'Petty Cash Settelment Report',
                        'res_model': 'kw_advance_claim_settlement',
                        'domain': [('create_date', '>=', dt1), ('create_date', '<=', dt2)],
                        'target': 'main',
                        'context': {'default_hide_btn_cancel': True, 'default_show_ra_button': False},
                    }
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form,tree',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'name': 'Petty Cash Settelment Report',
                        'res_model': 'kw_advance_claim_settlement',
                        'domain': ['&',
                                   '|', ('create_date', '>=', dt1), ('create_date', '<=', dt2),
                                   '|', ('empl_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|',
                                   ('empl_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                        'context': {'default_hide_btn_cancel': True, 'default_show_ra_button': False},
                    }
        elif self.applied_by == 'my':
            _, num_days = calendar.monthrange(self.year, int(self.month))
            first_day = datetime.date(self.year, int(self.month), 1)
            last_day = datetime.date(self.year, int(self.month), num_days)
            record_data = self.env['kw_advance_claim_settlement'].sudo().search(
                ['|', 
                '&', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                '&', ('payment_date', '>=', first_day), ('payment_date', '<=', last_day)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_claim_settlement_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_report_form').id

                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form,tree',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'name': 'Petty Cash Settelment Report',
                        'res_model': 'kw_advance_claim_settlement',
                        'domain': [('create_date', '>=', first_day), ('create_date', '<=', last_day)],
                        'target': 'main',
                    }
                else:
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form,tree',
                        'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                        'name': 'Petty Cash Settelment Report',
                        'res_model': 'kw_advance_claim_settlement',
                        'domain': ['&',
                                   '|', ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                   '|', ('empl_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   '|',
                                   ('empl_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                   ('create_uid', '=', self.env.user.employee_ids.user_id.id)],
                        'target': 'main',
                    }
        elif self.applied_by == 'employee':
            emp_id = self.employee_ids
            record_data = self.env['kw_advance_claim_settlement'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_claim_settlement_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_report_form').id
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'name': 'Petty Cash Settelment Report',
                    'res_model': 'kw_advance_claim_settlement',
                    'domain': [('empl_id', 'in', emp_id.ids)],
                    'target': 'main',
                }
        elif self.applied_by == 'all':
            record_data = self.env['kw_advance_claim_settlement'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_claim_settlement_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_report_form').id
                action = {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'name': 'Petty Cash Settlement Report',
                    'res_model': 'kw_advance_claim_settlement',
                    'target': 'main',
                }
                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    action['domain'] = []
                else:
                    action['domain'] = ['|',('empl_id', '=', self.env.user.employee_ids.id),('empl_id.parent_id', '=', self.env.user.employee_ids.id)]
                return action

    @api.onchange('applied_by')
    def onchange_employee_id(self):
        if self.applied_by == 'employee' and self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_user') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_admin') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group(
                'kw_employee.group_hr_ra'):
            raise ValidationError("You are not eligible for this Option")


class kw_emi_report_wizard(models.TransientModel):
    _name = 'kw_emi_report_wizard'
    _description = 'EMI Report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the EMI at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the EMI at that date")
    applied_by = fields.Selection([
        ('all','All'),
        ('dt', 'Date wise'),
        ('my', 'Month & Year wise'),
        ('employee', 'Employee'),
    ], string="Applied By", default='all')
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    year = fields.Selection(get_years(), string='Year')
    employee_ids = fields.Many2many('hr.employee', 'kw_emi_report_wiz_hr_employee_rel', 'emi_wiz_id', 'employee_id',
                                    string="Employee")

    @api.onchange('applied_by')
    def _get_employee(self):
        if self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group(
                    'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.has_group('kw_employee.group_hr_ra') and not self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_admin') or self.env.user.employee_ids.department_id.manager_id.user_id.id == self.env.user.employee_ids.user_id.id:
            domain = ['|', '|', ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                        ('id', '=', self.env.user.employee_ids.id)]
            employee_data = self.env['hr.employee'].sudo().search(domain)
        else:
            employee_data = self.env['hr.employee'].sudo().search([])
        return {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}


    def search_emi_report(self):
        self.ensure_one()
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            record_data = self.env['kw_advance_deduction_line'].sudo().search(
                ['|', 
                '&', ('deduction_date', '>=', dt1), ('deduction_date', '<=', dt2),('deduction_id','!=',False), 
                '&',('payment_date', '>=', dt1),('payment_date', '<=', dt2),('deduction_id','!=',False)])
            # print("record_data===",record_data)
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_emi_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_emi_form_report').id
                

                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form',
                    'name': 'EMI Report',
                    'res_model': 'kw_advance_deduction_line',
                    'target': 'main',
                    'domain': [('id','in',record_data.ids)],
                }
        elif self.applied_by == 'my':
            _, num_days = calendar.monthrange(self.year, int(self.month))
            first_day = datetime.date(self.year, int(self.month), 1)
            last_day = datetime.date(self.year, int(self.month), num_days)
            record_data = self.env['kw_advance_deduction_line'].sudo().search([('deduction_date', '>=', first_day),('deduction_date', '<=', last_day),('deduction_id','!=',False)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_emi_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_emi_form_report').id

                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form',
                    'name': 'EMI Report',
                    'res_model': 'kw_advance_deduction_line',
                    'target': 'main',
                    'domain': [('id','in',record_data.ids)],
                }
        elif self.applied_by == 'employee':
            emp_id = self.employee_ids
            record_data = self.env['kw_advance_deduction_line'].sudo().search([('deduction_id','!=',False)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_emi_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_emi_form_report').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form',
                    'name': 'EMI Report',
                    'res_model': 'kw_advance_deduction_line',
                    'domain': [('employee_id', 'in', emp_id.ids)],
                    'target': 'main',
                }
        elif self.applied_by == 'all':
            record_data = self.env['kw_advance_deduction_line'].sudo().search([('deduction_id','!=',False)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_advance_claim.kw_emi_tree_report').id
                form_view_id = self.env.ref('kw_advance_claim.kw_emi_form_report').id
                action = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form',
                    'name': 'EMI Report',
                    'res_model': 'kw_advance_deduction_line',
                    'target': 'main',
                    'context':{'search_default_group_by_deduction_id': 1},
                    'search_view_id': (self.env.ref('kw_advance_claim.search_view_emi').id,)
                }
                if self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account') or self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_admin'):
                    action['domain'] = [('id','in',record_data.ids),('deduction_id','!=',False)]
                else:
                    action['domain'] = ['|','&',('id','in',record_data.ids),('employee_id', '=', self.env.user.employee_ids.id),('employee_id.parent_id', '=', self.env.user.employee_ids.id),('deduction_id','!=',False)]
                return action

    @api.onchange('applied_by')
    def onchange_employee_id(self):
        if self.applied_by == 'employee' and self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_user') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_admin') and not self.env.user.has_group(
                'kw_advance_claim.group_kw_advance_claim_account') and not self.env.user.has_group(
                'kw_employee.group_hr_ra'):
            raise ValidationError("You are not eligible for this Option")
