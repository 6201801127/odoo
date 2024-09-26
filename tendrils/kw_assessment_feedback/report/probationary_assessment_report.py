from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
import calendar
from odoo.exceptions import ValidationError

class ProbationaryAssessmentReport(models.Model):
    _name = "kw_probationary_assessment_report"
    _description = "Final Report"
    _auto = False
    _rec_name = 'assessee'


    assessee            = fields.Char(string="Assessee")
    designation         = fields.Char(string="Designation")
    department          = fields.Char(string="Department")
    assessors           = fields.Text(string='Assessors',compute='_get_assessors')
    
    fst_assessment_date     = fields.Date(string="Date Of Assessment")
    fst_score               = fields.Char(string="Score (in %)")
    fst_weightage           = fields.Char(string="Performance Grade")
    fst_assessment_result   = fields.Selection(string='Assessment Result',selection=[('completed', 'Completed'),('extended', 'Extended'),
                                                                            ('failed_prob','Failed Probation Confirmation')])

    sec_assessment_date     = fields.Date(string="Date Of Assessment-2",compute='_get_probation_result')
    sec_score               = fields.Char(string="Score (in %)-2",compute='_get_probation_result')
    sec_weightage           = fields.Char(string="Performance Grade-2",compute='_get_probation_result')
    sec_assessment_result   = fields.Selection(string='Assessment Result-2',selection=[('completed', 'Completed'),('extended', 'Extended')],compute='_get_probation_result')

    trd_assessment_date     = fields.Date(string="Date Of Assessment-3",compute='_get_probation_result')
    trd_score               = fields.Char(string="Score (in %)-3",compute='_get_probation_result')
    trd_weightage           = fields.Char(string="Performance Grade-3",compute='_get_probation_result')
    trd_assessment_result   = fields.Selection(string='Assessment Result-3',selection=[('completed', 'Completed'),('extended', 'Extended')],compute='_get_probation_result')

    fst_periodic_result     = fields.Char(string='Periodic Assessment Result 1',compute='_get_periodic_result')
    sec_periodic_result     = fields.Char(string='Periodic Assessment Result 2',compute='_get_periodic_result')
    trd_periodic_result     = fields.Char(string='Periodic Assessment Result 3',compute='_get_periodic_result')

    positive_area           = fields.Text(string='Positive Area')
    weak_area               = fields.Text(string='Weak Area')
    suggestion_remark       = fields.Text(string='Suggestion')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select fd.id as id, 
                CONCAT(he.name,' (',he.emp_code,')') as assessee,
                dept.name as department,
                job.name as designation,
                fd.assessment_date AS fst_assessment_date,
                fd.total_score as fst_score, 
                fwm.value as fst_weightage,
                fd.prob_status AS fst_assessment_result,
                fd.positive_area as positive_area,
                fd.weak_area as weak_area,
                fd.suggestion_remark as suggestion_remark
                from kw_feedback_details fd
               	join kw_feedback_assessment fa on fa.id = fd.assessment_tagging_id and assessment_type = 'probationary'
				left join hr_employee he on he.id = fd.assessee_id
                left join kw_feedback_weightage_master fwm on fwm.id = fd.weightage_id
                LEFT OUTER JOIN hr_department dept on dept.id = he.department_id
                LEFT OUTER JOIN hr_job job on job.id = he.job_id
            ORDER BY id DESC
        )""" % (self._table))   

    @api.multi
    def _get_assessors(self):
        for record in self:
            details = self.env['kw_feedback_details'].browse(record.id)
            if details:
                for configs in details: 
                    values = ', '.join(str(user_names.name + ' ('+ user_names.emp_code +')') if user_names and user_names.emp_code else user_names.name for user_names in configs.assessor_id)
                    record.assessors = values
    
    @api.multi
    def _get_periodic_result(self):
        details_model = self.env['kw_feedback_details']
        for record in self:
            prob_record = details_model.browse(record.id)
            if prob_record:
                details = details_model.search([('assessment_tagging_id.assessment_type', '=', 'periodic'),
                                                ('assessee_id', '=', prob_record.assessee_id.id)], order='id desc')
                try:
                    if details:
                        for i in range(len(details)):

                            if i == 0:
                                record.fst_periodic_result = details[i].total_score
                            else:
                                record.fst_periodic_result = "Not Done"

                            if i == 1:
                                record.sec_periodic_result = details[i].total_score
                            else:
                                record.sec_periodic_result = "Not Done"

                            if i == 2:
                                record.trd_periodic_result = details[i].total_score
                            else:
                                record.trd_periodic_result = "Not Done"
                    else:
                        record.fst_periodic_result = "Not Done"
                        record.sec_periodic_result = "Not Done"
                        record.trd_periodic_result = "Not Done"
                except Exception as e:
                    # print('Probationary report error' ,e)
                    pass

    @api.multi
    def _get_probation_result(self):
        details_model = self.env['kw_feedback_details']
        for record in self:
            pass
            # prob_record = details_model.browse(record.id)
            # details = details_model.search([('assessment_tagging_id.assessment_type','=','probationary'),('assessee_id','=',prob_record.assessee_id.id)],order='id desc')
            # if details:
            #     for i in range(len(details)):

            #         if i == 1:
            #             record.sec_assessment_date = details[i].assessment_date
            #             record.sec_score = details[i].total_score
            #             record.sec_weightage = details[i].weightage_id.value
            #             record.sec_assessment_result = details[i].prob_status
            #         else:
            #             pass

            #         if i == 2:
            #             record.trd_assessment_date = details[i].assessment_date
            #             record.trd_score = details[i].total_score
            #             record.trd_weightage = details[i].weightage_id.value
            #             record.trd_assessment_result = details[i].prob_status
            #         else:
            #             pass
            # else:
                # pass

    @api.multi
    def view_assessee_feedback_details(self):
        self.ensure_one()
        view_id = self.env.ref('kw_assessment_feedback.kw_feedback_publish_feedback_form_view1').id
        return {
            'name': 'Assessee Feedback Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_feedback_details',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'new',
            'flags': {'mode': 'readonly', 'toolbar': False, 'action_buttons': False},
        }


class ProbationaryTakenAssessmentReport(models.Model):
    _name = "kw_probationary_assessment_employee_report"
    _description = "Probationary Report"
    _auto = False
    _rec_name = 'assessee'

    assessee = fields.Char(string="Employee Name")
    emp_code = fields.Char(string="Employee Code")
    designation = fields.Char(string="Designation")
    department  = fields.Char(string="Department") 
    division = fields.Char(string="Division")
    section = fields.Char(string="Section")
    practise = fields.Char(string="Practise")
    date_of_joining = fields.Date(string="Date of Joining")
    probation_complete_date = fields.Date(string="Probation Complete Due Date")
    total_assesses_count = fields.Integer(string="Total Assessment given")
    count_check = fields.Boolean(string="check count", compute="check_count_of_assesses", store=False)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
          SELECT 
                id, assessee,emp_code,date_of_joining,department,division,section,practise,designation,probation_complete_date,
                SUM(assesses_count) as total_assesses_count
            FROM (
                SELECT 
                    he.id as id, 
                    he.name as assessee,
                    he.emp_code as emp_code,
                    he.date_of_joining as date_of_joining,
                    (select name from hr_department where id = he.department_id) as department,
                    (select name from hr_department where id = he.division) as division,
                    (select name from hr_department where id = he.section) as section,
                    (select name from hr_department where id = he.practise) as practise,
                    (select name from hr_job where id = he.job_id) as designation,
                    he.date_of_completed_probation as probation_complete_date,
                    count(fd.assessee_id) 
                        filter(where 
                            (select id from hr_employee where id = fd.assessee_id)=
                            (select assessee_id from kw_feedback_details where feedback_status = '6' LIMIT 1)
                        ) as assesses_count 
                        FROM 
                            hr_employee he
                            left join kw_feedback_details fd on he.id = fd.assessee_id					   
                        WHERE 
                            he.active IS TRUE
                            AND he.on_probation IS TRUE
                            AND he.date_of_completed_probation::date BETWEEN date_trunc('day', CURRENT_DATE) AND date_trunc('day', CURRENT_DATE + interval '1 month')
                        GROUP BY 
                            he.id
                    ) AS subquery
                    GROUP BY 
                        id, assessee,emp_code,date_of_joining,department,division,section,
                        practise,designation,probation_complete_date
        )""" % (self._table))

    def check_count_of_assesses(self):
        for rec in self:
            if rec.total_assesses_count > 0:
                rec.count_check=True
            else:
                rec.count_check=False  
    
    def action_button_view_tree(self):
        for rec in self:
            view_id = self.env.ref('kw_assessment_feedback.kw_feedback_probationary_publish_feedback_tree_view').id
            return {
                'name':'Assessment',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'views': [(view_id, 'tree')],
                'res_model': 'kw_feedback_details',
                'view_id': view_id,
                'res_id': rec.id,
                'target': 'self',
                'domain': [('emp_code', '=', rec.emp_code)],
                'context': {'edit': False, 'create': False},
            }
