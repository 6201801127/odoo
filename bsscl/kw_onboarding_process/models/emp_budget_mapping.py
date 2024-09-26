from datetime import date, datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class BudgetMapping(models.Model):
    _name = 'hr.employee.budget.mapping'
    _description = 'Employee Budget Mapping Report'
    _auto = False
    _order = 'name'

    # sl_no = fields.Integer(string="Sl#")
    name = fields.Char(string="Name")
    requisition_type = fields.Selection(string='Budget Type',
                                        selection=[('treasury', 'Treasury Budget'), ('project', 'Project Budget')])
    emp_role = fields.Many2one('kwmaster_role_name', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Employee Category")
    emp_id = fields.Many2one("hr.employee", string="Emp id")
    emp_code = fields.Char(string='Employee Code')
    date_of_joining = fields.Date(string="Joining Date")
    job_branch_id = fields.Many2one('kw_res_branch', 'Branch/SBU')
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    employement_type = fields.Many2one("kwemp_employment_type", string="Type of employment")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
        SELECT  row_number() over() AS id,
        id AS emp_id,
		emp_code AS emp_code,
        job_id AS job_id,
        employement_type AS employement_type,
		date_of_joining AS date_of_joining,
		job_branch_id AS job_branch_id,
		department_id AS department_id,
        name AS name,
        budget_type AS requisition_type,
        emp_role AS emp_role,
        emp_category AS emp_category
        FROM hr_employee WHERE active = true AND employement_type != 5)"""
        self.env.cr.execute(query)

    @api.multi
    def button_budget_settings(self):
        form_view_id = self.env.ref("kw_onboarding.kw_employee_budget_map_tree_view").id
        return {
            'name': _('Budget Mapping Logs'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee.budget.mapping.log',
            'view_id': form_view_id,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', '=', self.emp_id.id)],
        }


class BudgetMappingWizard(models.TransientModel):
    _name = "hr.employee.budget_mapping_wizard_data"
    _description = "Budget Wizard"

    @api.model
    def default_get(self, fields):
        res = super(BudgetMappingWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        # print(self.env.context)
        res.update({'emp_rec': active_ids})
        return res

    emp_rec = fields.Many2many(comodel_name='hr.employee.budget.mapping', relation="hr_employee_budget_mapping_rel",
                               column1="employee_id", column2="budget_id", string='Employee Info')
    emp_role = fields.Many2one('kwmaster_role_name', string="Employee Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Employee Category")
    budget_effective_from = fields.Date(string='Effective From')

    def update_budget_record_employee(self):
        emp_query = ''
        query = ''
        emp_rec = []
        for rec in self.emp_rec:
            emp_rec.append(rec.emp_id)
        for record in emp_rec:
            if self.emp_role != record.emp_role or self.emp_category != record.emp_category:
                if self.emp_role and self.emp_category and self.budget_effective_from:
                    log_record = self.env['hr.employee.budget.mapping.log'].sudo().search(
                        [('employee_id', '=', record.id)])
                    budget_effective_from_o = datetime.strptime(str(self.budget_effective_from),
                                                                DEFAULT_SERVER_DATE_FORMAT).date()

                    # if employee has no log, create 1st record and update the new budget settings
                    if self.emp_role and self.emp_category and not log_record.exists() and record.emp_role and record.emp_category:
                        budget_effective_from = record.date_of_joining
                        effective_to = self.budget_effective_from - timedelta(days=1)
                        query = f"""INSERT INTO hr_employee_budget_mapping_log (employee_id, emp_role, emp_category, 
                        budget_effective_from, effective_to) VALUES ({record.id},{record.emp_role.id},{record.emp_category.id},
                        '{budget_effective_from}', '{effective_to}');"""
                        self._cr.execute(query)
                    elif log_record.exists():
                        record_to_update = log_record.filtered(lambda x: x.effective_to is False)
                        if record_to_update.budget_effective_from >= budget_effective_from_o:
                            raise ValidationError(
                                f"Please select effective from date after {record_to_update.budget_effective_from.strftime('%d-%b-%Y')}.")
                        # UPDATE TO DATE FOR OLD RECORD
                        if record_to_update:
                            effective_to = self.budget_effective_from - timedelta(days=1)
                            update_record = f"""UPDATE hr_employee_budget_mapping_log SET 
                            effective_to='{effective_to}' WHERE id = '{record_to_update.id}';"""
                            self._cr.execute(update_record)

                    # INSERT NEW RECORD FOR LOG
                    emp_role = self.emp_role.id if self.emp_role.id else False
                    emp_category = self.emp_category.id
                    budget_effective_from = self.budget_effective_from
                    query = f"""INSERT INTO hr_employee_budget_mapping_log (employee_id, emp_role, emp_category, 
                    budget_effective_from) VALUES ({record.id},{emp_role},{emp_category},'{budget_effective_from}');"""
                    self._cr.execute(query)

                    emp_query = f"update hr_employee set emp_role = {self.emp_role.id}, emp_category={self.emp_category.id} where id={record.id};"
                    self._cr.execute(emp_query)

    @api.onchange('emp_role')
    def _get_categories(self):
        role_id = self.emp_role.id
        self.emp_category = False
        return {'domain': {'emp_category': [('role_ids', '=', role_id)], }}
