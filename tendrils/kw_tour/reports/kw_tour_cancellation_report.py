from odoo import models, fields, api
from odoo import tools


class TourCancellationReport(models.Model):
    _name = 'kw_tour_cancellation_report'
    _description = 'Tour Cancellation Report'
    _auto = False

    name = fields.Char("Employee Name")
    designation = fields.Char("Designation")
    department = fields.Char("Department")
    division = fields.Char("Division")
    applied_on = fields.Datetime("Applied On")
    purpose = fields.Char("Purpose")
    # state = fields.Char("Status")
    state = fields.Selection(string="Status",
                             selection=[('Applied', 'Cancellation Applied'), ('Approved', 'Cancellation Approved'),
                                        ('Rejected', 'Cancellation Rejected')])
    action_taken_by = fields.Char("Action To Be Taken By")
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
                select tc.id, concat(a.name,' (',a.emp_code,')') as name, 
                c.name as designation,
                d.name as department,
                (select name from hr_department where id = a.division) as division,
                tc.create_date as applied_on, 
                tc.reason as purpose,
                af.id AS fiscal_year_id,
                tc.state as state,
                case
                when tc.state = 'Applied' then (select name from hr_employee where id = a.parent_id)
                end as action_taken_by
                    
                from kw_tour_cancellation tc  
                join hr_employee a  on a.id = tc.employee_id
                left join hr_department d on a.department_id = d.id
                left join account_fiscalyear af ON tc.create_date BETWEEN af.date_start AND af.date_stop
                left join hr_job c on a.job_id = c.id
                    )""")

    @api.multi
    def action_cancellation_details(self):
        form_view_id = self.env.ref('kw_tour.view_kw_tour_cancellation_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_cancellation',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
        }
