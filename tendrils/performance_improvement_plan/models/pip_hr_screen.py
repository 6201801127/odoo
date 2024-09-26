from datetime import datetime, date
import pytz
from odoo import models, fields, api
from odoo import tools
from odoo.exceptions import ValidationError


class PipHrReportEmployee(models.Model):
    _name = "pip_hr_employee_counselling"
    _description = "Employee Performance Counselling"
    _rec_name = "emp_id"
    _auto = False
    _order = 'id desc'

    # sbu_id = fields.Many2one('kw_sbu_master', string="SBU")
    reference = fields.Char(string="Reference")
    pp_id = fields.Many2one('performance_improvement_plan')
    raise_by_emp = fields.Many2one('hr.employee', string="Raised By")
    emp_id = fields.Many2one('hr.employee', string="Employee")
    emp_name = fields.Char(string="Employee Name", related="emp_id.name")
    emp_code = fields.Char(string="Employee code", related="emp_id.emp_code")
    emp_desg = fields.Many2one('hr.job', string="Designation", related="emp_id.job_id")
    department_id = fields.Many2one('hr.department', string='Department', related="emp_id.department_id")
    project_id = fields.Many2one('project.project', string="Project")
    project_code = fields.Char(string="Project Code", compute="_compute_project_code")
    reason = fields.Char(string="Reason")
    suggestion_pm = fields.Selection(string='Suggestion(PM/Reviewer)',
                                     selection=[('move_to_pip', 'Move to PIP'),
                                                ('discuss', 'Discussion with higher authority (SBU/Reviewer)')], )
    suggestion_head = fields.Selection(string='Suggestion(Practice/Division head/HOD)',
                                       selection=[('move_to_pip', 'Move to PIP'),
                                                  ('discuss', 'Discussion with higher authority (SBU/Reviewer)')], )
    status = fields.Selection([('Draft', 'Draft'), ('Applied', 'PIP Raised'),
                               ('Recommend PIP', 'Recommend Counselling'), ('Forward', 'Forward'),
                               ], string='Status')

    remark_pm_rev = fields.Text('Remarks(PM/Div.head)')
    remarks_sbu = fields.Text(string="Remarks(SBU)")
    sbu_suggest = fields.Selection(string="SBU Remark", selection=[('Close', 'Close'), ('RP', 'Recommend PIP')])
    hod_suggest = fields.Selection(string="HOD Remark", selection=[('Close', 'Close'), ('RP', 'Recommend PIP')])

    applied_date = fields.Date(string="Applied Date")
    take_action_date = fields.Date(string="Action Taken date")
    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By")
    pip_status = fields.Char(string="Status", compute="_get_status_pip_employee",store=False)
    suggestion = fields.Selection(string='Suggestion',
                                  selection=[('move_to_pip', 'Move to PIP'),
                                             ('discuss', 'Discussion with higher authority (SBU/Reviewer)')], )
    remark = fields.Selection(string="Approved Remark", selection=[('Close', 'Close'), ('RP', 'Recommend PIP')])
    final_decision = fields.Char(string="Final Closed Decision")
    # hr_final_decision = fields.Selection(string="Final Decision", selection=[('Employment_closed', 'Employment to be closed '), ('Continued', 'Continued')],)

    @api.depends('project_id')
    def _compute_project_code(self):
        for rec in self:
            if rec.project_id:
                rec.project_code = rec.project_id.code
            else:
                rec.project_code = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT   
                pp.reference AS reference,
                pp.id AS id,
                pp.id AS pp_id,
                pp.raised_by AS raise_by_emp,
                pp.employee_id AS emp_id,
                CASE WHEN pp.project_id IS NOT NULL THEN pp.project_id ELSE NULL END AS project_id,
                
                (SELECT STRING_AGG(name, ', ') FROM pip_reason_issue_config WHERE id = pr.reason_id) AS reason,
                CASE 
                    WHEN pp.suggestion_pm IS NOT NULL THEN pp.suggestion_pm
                    WHEN pp.suggestion IS NOT NULL THEN pp.suggestion
                    ELSE NULL
                END AS suggestion,
                CASE 
                    WHEN pp.suggestion_reviewer IS NOT NULL THEN pp.suggestion_reviewer 
                    WHEN pp.suggestion_reviewer_sbu IS NOT NULL THEN pp.suggestion_reviewer_sbu
                    ELSE NULL
                END AS remark,
                CASE 
                    WHEN pp.status = 'Recommend PIP' THEN 'PIP Raise' 
                    WHEN pp.status = 'Applied' THEN 'Applied Status'
                    WHEN pp.status = 'Draft' THEN 'Draft'
                    ELSE 'Closed' 
                END AS pip_status,
                pp.status as status,
                pp.suggestion_reviewer_sbu AS sbu_suggest,
                pp.suggestion_reviewer AS hod_suggest,
                pp.suggestion_pm AS suggestion_pm,
                pp.suggestion AS suggestion_head,
                pp.applied_date AS applied_date,
                pp.approved_user_id AS action_taken_by,
                CASE 
                    WHEN pp.remarks IS NULL THEN pp.remarks_pm
                    WHEN pp.remarks_pm IS NULL THEN pp.remarks
                    ELSE NULL
                END AS remark_pm_rev,
                pp.remarks AS remarks_sbu,
                pp.date_of_action AS take_action_date,
                CASE 
                    WHEN pcd.final_decision IS NOT NULL THEN pcd.final_decision
                    ELSE 'NA'
                END AS final_decision
                
            FROM performance_improvement_plan pp
            LEFT JOIN project_project AS pj ON pj.id = pp.project_id
            LEFT JOIN pip_reason_rel AS pr ON pr.pip_config_id = pp.id  
            LEFT JOIN kw_pip_counselling_details AS pcd ON pcd.assessee_id = pp.employee_id AND pcd.pip_ref_id=pp.id
            WHERE (pp.status = 'Recommend PIP' OR pp.status = 'Applied' OR pp.status = 'Closed' OR pp.status = 'Draft' OR pp.status = 'Recommend Training')
        )"""
        self.env.cr.execute(query)

    def _get_status_pip_employee(self):
        for record in self:
            pip_status = 'NA'
            # print('record.id >>> ', record, record.emp_id, record.id)
            raise_pip = self.env['performance_improvement_plan'].sudo().search(
                [('employee_id', '=', record.emp_id.id), ('id', '=', record.id)])
            training_pip = self.env['kw_training'].sudo().search([('pip_training_id.id','=',raise_pip.id)])
            training_plan = self.env['kw_training_plan'].sudo().search([('training_id','=',training_pip.id)])
            training_session = self.env['kw_training_schedule'].sudo().search([
                ('training_id', 'in', training_pip.ids)
            ])
            assessment_created = self.env['kw_training_assessment'].sudo().search([
                    ('training_id', 'in', training_pip.ids)
                ])
                
            assessment_completed = self.env['kw_skill_answer_master'].sudo().search([
            ('status', '=', 'Completed'),('set_config_id','=',assessment_created.assessment_id.id),
            ('emp_rel', '=', record.emp_id.id)], limit=1)

            if raise_pip.status and not training_pip and raise_pip.status == "Recommend PIP":
                pip_status = 'Counselling Recommended'

            elif assessment_completed:
                pip_status = 'Assessment Completed'

            elif training_session:
                pip_status = 'Training Started'
            elif training_plan and training_plan.state == 'approved':
                pip_status = 'Training Plan Approved'
            elif training_plan and training_plan.state == 'apply':
                pip_status = 'Training Planned'
            elif  training_pip and training_pip.state == 'draft':
                pip_status = 'Training Planned'
                
            # elif raise_pip.status and not training_pip and raise_pip.status == "Recommend PIP":
            #     pip_status = 'PIP Raised'
            elif raise_pip.status and not training_pip and raise_pip.status == "Recommend Training":
                pip_status = 'Training Recommended'
            elif raise_pip.status and not training_pip and raise_pip.status == "Applied":
                pip_status = 'PIP Raised'
            elif raise_pip.status and not training_pip and raise_pip.status == "Draft":
                pip_status = 'Draft'
            elif raise_pip.status and not training_pip and raise_pip.status == 'Closed':
                pip_status = 'PIP Closed'
            record_pip = self.env['kw_pip_counselling_details'].sudo().search([
                                                                               ('pip_ref_id', '=', raise_pip.id)])
            # print('record_pip >>> ', record_pip, record_pip.feedback_status)
            if record_pip:
                pip_status = dict(record_pip._fields['feedback_status'].selection).get(record_pip.feedback_status)
                # for rec in record_pip:
                #     if rec.feedback_status and rec.feedback_status == "0":
                #         pip_status = 'Not Scheduled'
                #     elif rec.feedback_status and rec.feedback_status == "1":
                #         pip_status = 'Scheduled'
                #     elif rec.feedback_status and rec.feedback_status == "2":
                #         pip_status = 'Feedback Received'
                #     elif rec.feedback_status and rec.feedback_status == '3':
                #         pip_status = 'Under Observation'
                #     elif rec.feedback_status and rec.feedback_status == '4':
                #         pip_status = 'Second Counselling'
                #     elif rec.feedback_status and rec.feedback_status == '5':
                #         pip_status = 'Observation Complete'
                #     elif rec.feedback_status and rec.feedback_status == '6':
                #         pip_status = 'PIP Closed'
                #     else:
                #         pip_status = 'Exit Process'
            else:
                record.pip_status = pip_status
            record.pip_status = pip_status

    def get_view_details_user(self):
        form_view = self.env.ref('performance_improvement_plan.kw_pip_user_details_form_view').id
        record = self.env['kw_pip_counselling_details'].sudo().search(
            [('assessee_id', '=', self.emp_id.id), ('pip_ref_id', '=', self.pp_id.id), ('feedback_status', 'in', ['3', '4', '6'])])
        # print('record >>> ', record)
        if record:
            action = {
                'name': 'PIP Reports',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_pip_counselling_details',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view,
                'target': 'self',
                'res_id': record.id,
                'context': {'create': False, 'edit': True, 'delete': False}
            }
            return action

        record_raised = self.env['performance_improvement_plan'].search(
            [('status', 'not in', ['Closed','Recommend Training']), ('employee_id', '=', self.emp_id.id), ('id', '=', self.pp_id.id)])
        # print('record_raised >>> ', record_raised, self.emp_id.id, self.pp_id.id)
        if record_raised:
            raise ValidationError("Your PIP Process is Raised, after counselling you can view the details.")
        else:
            raise ValidationError("Your PIP Process is Raised, after training you can view the details.")
            

    def get_view_report(self):
        form_view = self.env.ref('performance_improvement_plan.performance_improvement_plan_takeaction_form').id
        action = {
            'name': 'PIP Details',
            'type': 'ir.actions.act_window',
            'res_model': 'performance_improvement_plan',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view,
            'target': 'self',
            'res_id': self.id,
            'context': {'create': False, 'edit': False, 'delete': False}
        }
        return action

    def take_action_of_hr(self):
        view_id = self.env.ref('performance_improvement_plan.pip_counselling_config_form').id
        record = self.env['kw_pip_counselling_details'].sudo().search(
            [('assessee_id', '=', self.emp_id.id), ('pip_ref_id', '=', self.pp_id.id)])
        if self.pip_status not in ['NA', 'PIP Closed']:
            action = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_pip_counselling_details',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'res_id': record.id if record else '',
                'context': {'create': False, 'edit': True, 'delete': False,
                            'default_assessee_id': self._context.get('current_emp'),
                            'default_reference': self._context.get('ref_no'),
                            'default_pip_ref_id': self._context.get('pip_refid')}
            }
            return action
        else:
            return {}

        # }
        # counselling_details = self.env['kw_pip_counselling_details'].create({
        #     'assessee_id': self.emp_id.id,
        # })
        # url = f'/web#action={action_id}&model=kw_pip_counselling_details&view_type=form&id={counselling_details.id}'
        # # pip_counselling_rec = self.env['kw_pip_counselling_details'].sudo().search([('assessee_id','=',self.emp_id.id),('feedback_status', '!=', '4')])
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': url,
        #     'target': 'self',
        #     'tag': 'form',

        # }

    @api.model
    def get_pip_report_view_data(self):
        tree_view_id = self.env.ref('performance_improvement_plan.performance_improvement_plan_all_report_list').id
        form_view_id = self.env.ref('performance_improvement_plan.performance_improvement_plan_all_report_form').id
        action = {
            'name': 'PIP Process Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'pip_hr_employee_counselling',
            'views': [(tree_view_id, 'tree'),(form_view_id, 'form',)],
            'target': 'self',
            'domain': []
        }
        # PIP User
        if (self.env.user.has_group('performance_improvement_plan.group_pip_module_user')
                and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')
                and not self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
                and not self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user')):
            # print("PIP User=====================================")
            action['domain'] = [('emp_id', '=', self.env.user.employee_ids.id)]
        elif self.env.user.has_group('performance_improvement_plan.group_pip_mis_user') :
            # print("PIP report manager=====================================")
            action['domain'] = ['|','|','|','|',('raise_by_emp.id', '=', self.env.user.employee_ids.id),('raise_by_emp.id', '!=', self.env.user.employee_ids.id),('emp_id.department_id.manager_id', '=', self.env.user.employee_ids.id),
                                ('emp_id', '=', self.env.user.employee_ids.id),('project_id.sbu_id.representative_id', '=', self.env.user.employee_ids.id)]
        # PIP HR User
        # elif (self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
        #       and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')):
        #     print("PIP HR manager=====================================")

        elif (self.env.user.has_group('kw_resource_management.group_sbu_representative')
              and self.env.user.has_group('performance_improvement_plan.group_pip_user')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
              and not self.env.user.has_group('kw_wfh.group_hr_hod')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')
              and (self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user')
                   or not self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user'))
              and (not self.env.user.has_group('kw_employee.group_hr_ra')
                   or self.env.user.has_group('kw_employee.group_hr_ra'))):
            # print("ist if==============sbu=====================")
            tree_view_id = self.env.ref('performance_improvement_plan.performance_improvement_plan_report_list').id
            # form_view_id = env.ref('performance_improvement_plan.performance_improvement_plan_report_form').id
            action = {
                'name': 'PIP Report',
                'type': 'ir.actions.act_window',
                'view_mode': 'form,tree',
                'res_model': 'pip_hr_employee_counselling',
                'views': [(tree_view_id, 'tree'), ],
                'domain': ['|', '|', '|',
                           ('project_id.sbu_id.representative_id', '=', self.env.user.employee_ids.id),
                           ('raise_by_emp.id', '=', self.env.user.employee_ids.id),
                           ('emp_id.sbu_master_id', '=', self.env.user.employee_ids.id),
                           ('emp_id', '=', self.env.user.employee_ids.id)]
            }
        elif (self.env.user.has_group('kw_wfh.group_hr_hod')
              and (self.env.user.has_group('performance_improvement_plan.group_pip_user')
                   or not self.env.user.has_group('performance_improvement_plan.group_pip_user'))
              and (self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user')
                   or not self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user'))
              and not self.env.user.has_group('kw_resource_management.group_sbu_representative')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')):
            # print("2nd if=========hOD===================================")
            action['domain'] = ['|', '|', ('raise_by_emp.id', '=', self.env.user.employee_ids.id),
                                ('emp_id.department_id.manager_id', '=', self.env.user.employee_ids.id),
                                ('emp_id', '=', self.env.user.employee_ids.id)]

        elif (self.env.user.has_group('kw_employee.group_hr_ra')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_user')
              and (self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user')
                   or not self.env.user.has_group('performance_improvement_plan.group_pip_assessor_user'))
              and not self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')
              and (not self.env.user.has_group('kw_wfh.group_hr_hod')
                   or self.env.user.has_group('kw_wfh.group_hr_hod'))
              and not self.env.user.has_group('kw_resource_management.group_sbu_representative')):
            # print("in ra=====================")

            action['domain'] = [('emp_id.parent_id', '=', self.env.user.employee_ids.id)]

        elif (self.env.user.has_group('performance_improvement_plan.group_pip_user')
              and not self.env.user.has_group('kw_resource_management.group_sbu_representative')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_manager')
              and not self.env.user.has_group('performance_improvement_plan.group_pip_hr_user')
              and not self.env.user.has_group('kw_wfh.group_hr_hod')):
            # print("========in pm==========")
            action['domain'] = ['|', '|', ('raise_by_emp.id', '=', self.env.user.employee_ids.id),
                                ('emp_id', '=', self.env.user.employee_ids.id),
                                ('project_id.emp_id', '=', self.env.user.employee_ids.id)]

        return action

    # def get_hide_view_details(self):
    #     record = self.env['kw_pip_counselling_details'].sudo().search([('assessee_id','=',self.emp_id.id)])
    #     if not record:
    #         self.hide_view_details_check = True
    # @api.multi
    # def meeting_manage_emp(self):
    #     form_view_id = self.env.ref('performance_improvement_plan.pip_counselling_take_action')
    #     return {
    #         'name': "Counselling Details",
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'view_id': form_view_id,
    #         'target': 'new',
    #         'res_model': 'kw_pip_remark_wizard',
    #         'type': 'ir.actions.act_window',
    #     }
    def button_employee_pip_details(self):
        form_view_id = self.env.ref('performance_improvement_plan.kw_pip_feedback_hr_view_feedback_form_view').id
        record = self.env['kw_pip_counselling_details'].sudo().search([('assessee_id', '=', self.emp_id.id), ('pip_ref_id', '=', self.pp_id.id),('reference','=',self.reference)])
        return {
            'name': "Counselling Details",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'res_model': 'kw_pip_counselling_details',
            'type': 'ir.actions.act_window',
            'res_id': record.id,
            'domain': [],
            'context': {'create': False, 'edit': False, 'delete': False,},
        }


class ScheduleCounsellingLog(models.Model):
    _name = "counselling_configuration_log"
    _description = "counselling configuration log of employee"

    config_details_id = fields.Many2one('kw_pip_counselling_details', string='Meeting Name')
    meeting_id = fields.Many2one('kw_meeting_events')
    meeting_date = fields.Date(related='meeting_id.kw_start_meeting_date')
    meeting_time = fields.Selection(related='meeting_id.kw_start_meeting_time')
    meeting_duration = fields.Selection(related='meeting_id.kw_duration')
    meeting_room = fields.Many2one(comodel_name='kw_meeting_room_master', related='meeting_id.meeting_room_id')
