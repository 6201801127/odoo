from odoo import models, api, fields ,tools
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError



class kw_cpd_applicants_report(models.Model):
    _name = 'kw_cpd_applicants_report'
    _rec_name = 'employee_id'
    _auto = False
    _order = 'applied_date DESC'


    cpd_id = fields.Many2one('kw_cpd_applications')
    cpd_certification_id = fields.Many2one('kw_cpd_certification')

    employee_id = fields.Many2one('hr.employee', string="Employee Name")
    institute_id = fields.Many2one('kw_institute_master', string="Institute Name")
    course_id = fields.Many2one('kw_course_master', string="Course Name")
    course_duration = fields.Integer(string='Course Duration (In Days)')
    course_fee = fields.Float(string='Course Fee (INR)')
    to_disburse_course_fee = fields.Float(string='Disbursement Amount (INR)')
    description = fields.Text(required=True)
    applied_date = fields.Date()
    status = fields.Char('Status')





    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT 
                row_number() OVER () AS id,
                id AS cpd_id,
                cpd_certification_id as cpd_certification_id,
                employee_id AS employee_id,
                institute_id AS institute_id,
                course_id AS course_id,
                course_duration AS course_duration,
                course_fee AS course_fee,
                to_disburse_course_fee AS to_disburse_course_fee,
                description AS description,
                applied_date AS applied_date,
                                        
                CASE 
                    WHEN state = 5 THEN 
                        CASE 
                            WHEN cpd_certification_id IS NULL THEN 'Course Approved'
                            ELSE (SELECT 
                                    CASE
                                        WHEN state = 0 THEN 'Certification at Draft'
                                        WHEN state = 1 THEN 'Certification Pending at L&K'
                                        WHEN state = 2 THEN 'Certification Pending at CORE HR'
                                        WHEN state = 3 THEN 'Certification Pending at FINANCE'
                                        WHEN state = 4 THEN 'Disbursed'
                                        WHEN state = 5 THEN 'Certification Rejected'
                                    END
                                FROM kw_cpd_certification 
                                WHERE id = cpd_certification_id)
                        END
                    ELSE
                        CASE 
                            WHEN state = 0 THEN 'Course at Draft'
                            WHEN state = 1 THEN 'Course Pending at RA'
                            WHEN state = 2 THEN 'Course Pending at Dept Head'
                            WHEN state = 3 THEN 'Course Pending at L&K'
                            WHEN state = 4 THEN 'Course Pending at CHRO'
                            WHEN state = 6 THEN 'Course Rejected'
                            WHEN state = -1 THEN 'Course on Hold'
                        END
                END AS status
                                        
            FROM kw_cpd_applications
            WHERE state NOT IN (0)


                            
                
            )""" % (self._table))
        


    def kw_cpd_view_application(self):
        view_id = self.env.ref("kw_cpd.kw_cpd_application_apply_form").id
        action = {
            'name': 'CPD Report',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_cpd_applications',
            'res_id': self.cpd_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': {'edit': False, 'create': False, 'delete': False}
        }
        return action 
    

    def kw_cpd_view_certification(self):
        view_id = self.env.ref("kw_cpd.kw_cpd_certification_form").id
        action = {
            'name': 'CPD Report',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_cpd_certification',
            'res_id': self.cpd_certification_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'current',
            'context': {'edit': False, 'create': False, 'delete': False}
        }
        return action 