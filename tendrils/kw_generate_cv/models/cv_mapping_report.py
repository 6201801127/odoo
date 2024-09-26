# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class ForecastedReleaseReport(models.Model):
    _name = 'cv_mapping_report'
    _description = 'CV Mapping Report'
    _auto = False


    sequence= fields.Char(string='Request Code')
    account_holder = fields.Many2one('hr.employee')
    resource_name = fields.Many2one('hr.employee')
    emp_id = fields.Many2one('hr.employee')
    designation = fields.Many2one('hr.job')
    project = fields.Many2one('crm.lead')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    state = fields.Char('State')
        

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (

        select row_number() over() AS id,
        m.sequence as sequence,
        m.account_holder as account_holder,
        cv.report_id as resource_name,
        cv.emp_id as emp_id,
        m.job_id as designation,
        m.project as project,
        m.effective_from_date as from_date,
        m.effective_to_date as to_date,
        m.state as state
        from hr_cv_mapping as m
        left join hr_cv_mapping_employee as cv on cv.emp_id = m.id
        left join hr_employee as hr on hr.id = m.id
        )""" )


