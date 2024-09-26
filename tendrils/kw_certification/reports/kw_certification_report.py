from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime


class CertificationReport(models.Model):
    _name = 'kw_certification_report'
    _description = 'Certification Report'
    _auto = False

    number = fields.Char('Sequence Number')
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    certification_id = fields.Many2one('kwmaster_stream_name', string='Certification Name')
    require_department_id = fields.Many2one('hr.department', string='For Department')
    technology_id = fields.Many2one('kw_skill_master', 'Technology')
    # dept_head = fields.Many2one('hr.employee')
    create_date = fields.Datetime('Create Date')
    raised_by_id = fields.Many2one('hr.employee', 'Raised By')
    target_date = fields.Date('Target Date')
    achieve_date = fields.Date('Achieve Date')
    state = fields.Char('Status')
    year = fields.Char()
    month = fields.Char()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    select row_number() over() as id,
                        kc.number as number,
                        agm.employee_id as employee_id,
                        kc.certification_type_id as certification_id, 
                        kc.require_department_id as require_department_id,
                        kc.technology_id as technology_id,
                        kc.raised_by_id as raised_by_id,
                        kc.target_date as target_date,
                        kc.achieve_date as achieve_date,
                        kc.create_date as create_date,
                        kc.state as state,
                        EXTRACT(YEAR FROM kc.create_date) AS year,
                        EXTRACT(MONTH FROM kc.create_date) as month
                    
                    from kw_certification  as kc
                    join assign_employee as agm
                    on kc.id = agm.certification_master_id where kc.state != 'Draft'

        )"""
        self.env.cr.execute(query)



    