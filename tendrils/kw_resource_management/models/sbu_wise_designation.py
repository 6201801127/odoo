from odoo import models, fields, api
from odoo import tools

class SbuWiseDesignation(models.Model):
    _name = "sbu_wise_designaiton"
    _description = "SBU Wise Desigantion report"
    _auto = False


    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name= fields.Char(related='sbu_id.name', string='SBU')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    name = fields.Char(related='employee_id.name',string='Name')
    designation = fields.Many2one('hr.job',string='Designation')
    # emp_role = fields.Many2one('kwmaster_role_name',string='Role')
    # emp_category = fields.Many2one('kwmaster_category_name',string='Category')
    # employement_type = fields.Many2one('kwemp_employment_type',string='Type')
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            
            SELECT row_number() OVER () AS id,
            hr.sbu_master_id AS sbu_id,
            hr.sbu_type AS sbu_type,
            hr.job_id AS designation,
            hr.id as employee_id
        --     case when kcn.code in ('TTL', 'PM') then hr.name
        --     end as name
            FROM hr_employee AS hr
            JOIN hr_department AS hrd ON hrd.id = hr.department_id
        -- 	LEFT JOIN kwmaster_category_name kcn ON kcn.id = hr.emp_category
            WHERE hr.active = TRUE
                AND hrd.code = 'BSS'
                AND hr.employement_type NOT IN (SELECT id FROM kwemp_employment_type WHERE code = 'O')
                AND hr.sbu_type = 'sbu'
                AND hr.sbu_master_id IS NOT NULL
                and hr.job_id in (366,540,365,484,545,1267,539,376)

		
                )"""
        self.env.cr.execute(query)
