# -*- coding: utf-8 -*-
"""
Module: Internship Program Report

Summary:
    This module contains the InternshipProgramReport class, which represents a model for generating internship program reports.

Description:
    The InternshipProgramReport class defines a model used for generating reports related to internship programs.
    It provides functionalities for querying and aggregating data to produce detailed reports on internship activities.

"""
from odoo import models, fields, api
from odoo import tools
from datetime import date, datetime


class InternshipProgramReport(models.Model):
    """
    Model for generating internship program reports.

    This class represents a model used for generating reports related to internship programs.

    Attributes:
        _name (str): The technical name of the model.
    """

    _name = "internship_program_report"
    _description = "Internship Program Report"
    _auto = False

    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year')
    batch_name = fields.Char(string="Batch no")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_name = fields.Char(string="Name")
    employee_code = fields.Char(string="Emp Code")
    job_id = fields.Many2one('hr.job', string='Designation')
    date_of_joining = fields.Date(string="Date of Joining")
    location = fields.Many2one("kw_res_branch", string="Location")
    foundation_program_status = fields.Char(string="Foundation Prog.",
                                            compute='_foundation_program_status_string_Change')
    foundation_program_score = fields.Float(string="Score")
    foundation_completion_date = fields.Date(string="Completion Date")
    internship_program_status = fields.Char(string="Internship Prog.")

    internship_program_score = fields.Float(string="Score")
    internship_completion_date = fields.Date(string="Completion Date")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    SELECT bd.id as id,
                    lb.financial_year_id AS financial_year_id ,
                    lb.name as batch_name,
                    he.name AS employee_name,
                    he.emp_code AS employee_code,
                    he.job_id AS job_id,
                    he.date_of_joining AS date_of_joining,
                    he.job_branch_id AS location,
                    --bd.traineeship_status AS foundation_program_status,
                    bd.traineeship_score AS foundation_program_score,
                    bd.traineeship_completion_date AS foundation_completion_date,
                    bd.employee_id as employee_id,
                    CASE WHEN (bd.internship_score >= 60) THEN 'Completed'
                      WHEN (bd.internship_score >= 50 and bd.internship_score < 60 ) THEN 'Hold' 
                      WHEN (bd.internship_score > 0 and bd.internship_score <50) THEN 'Close'
                      WHEN (bd.internship_score < 1) THEN 'Continuing'  
                      ELSE '---' END AS internship_program_status,
                    bd.internship_score AS internship_program_score,
                    bd.internship_completion_date AS internship_completion_date
                    FROM lk_batch_details bd
                    LEFT JOIN lk_batch lb ON bd.batch_id = lb.id 
                    LEFT JOIN hr_employee he ON he.id = bd.employee_id
					          
          )"""
        # concat(h.name,', ',h.designation_name)
        # print("tracker query===========================================================================",query)
        self.env.cr.execute(query)

        #  CASE WHEN (bd.traineeship_score >= 60) THEN 'Completed'
        #                       WHEN (bd.traineeship_score >= 50 and bd.traineeship_score < 60 ) THEN 'Hold'
        #                       WHEN (bd.traineeship_score > 0 and bd.traineeship_score < 50) THEN 'Close'
        #                       ELSE 'Continuing' END AS foundation_program_status,

    def _foundation_program_status_string_Change(self):
        for rec in self:
            traineeship_data = self.env['lk_batch_details'].sudo().search(
                [('employee_id', '=', rec.employee_id.id)]).mapped('traineeship_status')
            # print("traineeship_statuses======================", traineeship_data)
            resignation_data = self.env['kw_resignation'].sudo().search(
                [('user_id.employee_ids.id', '=', rec.employee_id.id)])
            # print(resignation_data,"resignation_data----------------->>>>>>>>>>>>>>>>>>>>>")

            if 'Approved' in traineeship_data and not resignation_data:
                rec.foundation_program_status = 'Completed'
                # print(rec.foundation_program_status, "rec.foundation_program_status======================")
            else:
                # print("in else condition=============================")
                rec.foundation_program_status = 'Not Completed'
