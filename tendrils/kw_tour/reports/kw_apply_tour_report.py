from odoo import models, fields, api
from odoo import tools


class ApplyTourReport(models.Model):
    _name = 'kw_apply_tour_report'
    _description = 'Tour Apply Report'
    _auto = False

    tour_id = fields.Many2one("kw_tour", "Tour")
    tour_type_id = fields.Many2one("kw_tour_type_new", "Tour Type")
    name = fields.Char("Employee Name")
    desg = fields.Char("Designation")
    dept_name = fields.Char("Department")
    division = fields.Char("Division")
    tour_type = fields.Char("Tour Type")
    project = fields.Char("Project")
    date_of_travel = fields.Date("Date Of Travel")
    date_of_return = fields.Date("Date Of Return")
    purpose = fields.Char("Purpose")
    origin_place = fields.Char("Originating Place")
    state = fields.Char("Status")
    action_taken_by = fields.Char("Action To Be Taken By", related="tour_id.pending_at")
    actual_project_id = fields.Many2one('project.project', string="Project")
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
            select b.id,b.id as tour_id, concat(a.name,' (',a.emp_code,')') as name, 
            c.name as desg,
            d.name as dept_name,
            (select name from hr_department where id = a.division) as division,
            tour_type.name as tour_type,
            project.name as project,
            b.date_travel as date_of_travel, 
            e.name as origin_place, 
            b.tour_type_new as tour_type_id,
            b.date_return as date_of_return,
            b.purpose as purpose,
            b.actual_project_id,
            af.id AS fiscal_year_id,
            case when  exists(select id from kw_tour_cancellation where tour_id = b.id and state='Applied') then 'Cancellation Applied' else b.state end as state

            from kw_tour b  
            join hr_employee a  on a.id = b.employee_id
            left join kw_tour_type tour_type  on b.tour_type_id = tour_type.id
            left join crm_lead project on b.project_id = project.id
            left join account_fiscalyear af ON b.date_travel BETWEEN af.date_start AND af.date_stop
            left join hr_department d on a.department_id = d.id
            left join hr_job c on a.job_id = c.id
            left join kw_tour_city e on  b.city_id = e.id
            where b.state != 'Draft'
                    )""")

    @api.multi
    def action_tour_details(self):
        form_view_id = self.env.ref('kw_tour.view_kw_tour_view_all_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
        }
