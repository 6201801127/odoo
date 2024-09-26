from odoo import models, fields, api
from odoo.exceptions import ValidationError




class ReportAccessGroups(models.Model):
    _name = 'kw_report_access_groups'
    _description = "Report Access Groups"
    _rec_name = "name"

    name = fields.Char('Name')

    group_users_ids = fields.One2many('kw_report_access_groups_lines', 'report_access_group_id', string= 'Group Access')
    manager_report_access = fields.Boolean('Manager Report Access')
    users_ids = fields.Many2many('hr.employee', 'kw_report_access_groups_rel', 'employee_id', 'sbu_emp_id',
                                 string="Users")


    def update_user_access(self):
        m_data = []
        for emp in self.users_ids:
            m_data.append(emp.user_id.id)
        print(m_data, 'm_data')
        group_manager_report = self.env.ref('kw_budget.group_manager_report').sudo()
        group_manager_report.write({'users': [(6, 0, m_data)]})
        if self.group_users_ids:
            for rec in self.group_users_ids:
                dataa = []
                if rec.group_name == 'Annual Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_annual_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})

                if rec.group_name == 'Treasury Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_treasury_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})

                if rec.group_name == 'Capital Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_capital_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})

                if rec.group_name == 'Revenue Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_revenue_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})

                if rec.group_name == 'Project Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_project_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})

                if rec.group_name == 'Cash Flow Report':
                    for employee_id in rec.users_ids:
                        dataa.append(employee_id.user_id.id)
                    group_annual_report = self.env.ref('kw_budget.group_cash_report').sudo()
                    group_annual_report.write({'users': [(6, 0, dataa)]})
        # if self.manager_report_access:


        else:
            raise ValidationError('Please add Group Access details.')

class ReportAccessGroupsLines(models.Model):
    _name = 'kw_report_access_groups_lines'
    _description = "Report Access Groups Lines"
    _rec_name = "group_name"

    name = fields.Char('Name')
    group_name = fields.Selection(string="Group Name",
                     selection=[('Treasury Report', 'Treasury Report'),
                                ('Capital Report', 'Capital Report'),
                                ('Project Report', 'Project Report')])

    users_ids = fields.Many2many('hr.employee', 'kw_sbu_approver_user_rel', 'employee_id', 'sbu_emp_id',
                                        string="Users", required=True)

    report_access_group_id = fields.Many2one('kw_report_access_groups', string='report_access_group_id')
