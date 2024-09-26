from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class EmployeeHealthInsuranceEmiDetails(models.Model):
    _name = 'emp_health_insurance_emi_details_report'
    _description = 'Employee Health Insurance EMI Details Report'
    _auto = False

    date_range = fields.Many2one('account.fiscalyear', 'Financial Year',)
    year = fields.Char(string='Year',size=4)
    month = fields.Char(string='Month')
    emp_name = fields.Char(string="Name")
    emp_code = fields.Char(string="Code")
    installment = fields.Float(string='Installment')
    emi_status = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')], string="EMI Status")
    insurance_status = fields.Selection(string="Insurance Status",
                             selection=[('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'),
                                        ('closed', 'Closed')], default='draft', track_visibility='onchange')
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            select 
                row_number() over(order by e.name) as id,
                h.date_range as date_range,
                emi.year as year,
                emi.month as month, 
                e.emp_code as emp_code,
                e.name as emp_name,
                emi.installment as installment,
                emi.status as emi_status,
                h.state as insurance_status
                from health_insurance_dependant as h
                join health_insurance_emi as emi
                on emi.emi_details_id = h.id
                join hr_employee e 
                on e.id=h.employee_id
                order by emi.emi_date,e.name
            )""" % (self._table))

                # where h.state in ('approved','closed')