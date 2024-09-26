# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class kw_appraisal(models.Model):
    _name = 'kw_appraisal'
    _description = 'Appraisal'
    _rec_name = 'year'

    emp_strt_date = fields.Date(string="Employee Start Date", required=True, autocomplete="off")
    emp_end_date = fields.Date(string="Employee End Date", required=True, autocomplete="off")
    lm_start_date = fields.Date(string='LM Start Date', required=True, autocomplete="off")
    lm_end_date = fields.Date(string='LM End Date', required=True, autocomplete="off")
    ulm_start_date = fields.Date(string='ULM Start Date', required=True, autocomplete="off")
    ulm_end_date = fields.Date(string='ULM End Date', required=True, autocomplete="off")
    employee = fields.Many2many(
        'kw_appraisal_employee', 'rel_appraisal', string='Employee', required=True)
    year = fields.Many2one('kw_assessment_period_master',
                           string='Appraisal Period', required=True, ondelete='restrict')
    hr_appraisal_ids = fields.One2many(
        'hr.appraisal', 'kw_appraisal_id', 'Hr Appraisal IDS')

    hr_state_id = fields.Boolean(string="Status", compute='_compute_hr_state_id')

    @api.multi
    def _compute_hr_state_id(self):
        for record in self:
            hr_state = self.env['hr.appraisal'].search([('appraisal_year_rel','=',record.year.id)])
            if hr_state:
                record.hr_state_id = True
            else:
                record.hr_state_id = False

    # @api.multi
    # def unlink(self):
    #     obj = self.env['kw_appraisal_employee'].search([('employee', 'in', self.ids)])
    #     if obj:
    #         raise ValueError("You are trying to delete a record that is still referenced!")
    #     return super(kw_appraisal, self).unlink()​

    @api.multi
    @api.constrains('year')
    def check_year(self):
        existing_record = self.env['kw_appraisal'].sudo().search([]) - self
        for record in existing_record:
            exist_year = record.year.ids
            if str(self.year.id) in str(exist_year):
                raise ValidationError("Appraisal period already exists.")

    @api.multi
    @api.constrains('emp_strt_date', 'emp_end_date')
    def date_constrains(self):
        for rec in self:
            if rec.emp_end_date < rec.emp_strt_date:
                raise ValidationError('Sorry, Self Appraisal End Date Must be greater Than Start Date...')

    @api.multi
    @api.constrains('lm_start_date', 'lm_end_date')
    def lmdate_constrains(self):
        for rec in self:
            if rec.lm_end_date < rec.lm_start_date:
                raise ValidationError('LM Appraisal End Date Must be greater Than Start Date...')

    @api.multi
    @api.constrains('ulm_start_date', 'ulm_end_date')
    def ulmdate_constrains(self):
        for rec in self:
            if rec.ulm_end_date < rec.ulm_start_date:
                raise ValidationError('ULM Appraisal End Date Must be greater Than Start Date...')

    @api.model
    def create(self, values):
        record = super(kw_appraisal, self).create(values)
        if record:
            self.env.user.notify_success(message='Appraisal Period Configure Created Successfully.')
        # record.create_appraisal_employees()
        return record

    @api.multi
    def write(self, values):
        self.ensure_one()
        super(kw_appraisal, self).write(values)
        self.env.user.notify_success(message='Appraisal Period Configure Updated Successfully.')
        # if values.get('hr_appraisal_ids', False):
        #     appraisal_ids = self.create_appraisal_employees()
        return True
    def calculate_training_score(self,current_fiscal_year,employee):
        current_fy = current_fiscal_year
        training_percentage = planned_training_hours=achieved_duration=0
        if current_fy:
            self.env.cr.execute(f"SELECT TO_CHAR(INTERVAL '1 second' * SUM(EXTRACT(EPOCH FROM (ks.to_time::time - ks.from_time::time))), 'HH24:MI:SS') AS training_planned_hours FROM kw_training kt join kw_training_plan ktp on ktp.training_id=kt.id join kw_training_schedule ks ON kt.id=ks.training_id join hr_employee_kw_training_plan_rel hk ON hk.kw_training_plan_id = ktp.id JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop  where hk.hr_employee_id = {employee.id} and af.id = {current_fy.id} GROUP BY af.name,hk.hr_employee_id")
            planned_dict = self._cr.dictfetchall()
            self.env.cr.execute(f"SELECT TO_CHAR(INTERVAL '1 second' * SUM( CASE WHEN ktd.attended THEN EXTRACT(EPOCH FROM (ka.to_time::time - ka.from_time::time)) ELSE 0 END), 'HH24:MI:SS') AS attended_hours FROM kw_training kt JOIN account_fiscalyear af ON kt.create_date BETWEEN af.date_start AND af.date_stop JOIN kw_training_attendance ka ON ka.training_id = kt.id JOIN kw_training_attendance_details ktd ON ktd.attendance_id = ka.id where  af.id = {current_fy.id} and ktd.participant_id={employee.id} GROUP BY af.name, ktd.participant_id")
            duration_dict = self._cr.dictfetchall()
            if planned_dict:
                planned_training_hours = planned_dict[0]['training_planned_hours']
            if duration_dict:
                achieved_duration = duration_dict[0]['attended_hours']
                if achieved_duration and planned_training_hours:
                    def time_str_to_timedelta(time_str):
                        hours, minutes, seconds = map(int, time_str.split(':'))
                        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    planned_hours = time_str_to_timedelta(planned_training_hours)
                    attended_hours = time_str_to_timedelta(achieved_duration)
                    if attended_hours.total_seconds() != 0:
                        training_percentage = (attended_hours.total_seconds() / planned_hours.total_seconds()) * 100
        return training_percentage,planned_training_hours,achieved_duration
    @api.multi
    def action_start_appraisal_all(self):
        self.ensure_one()
        start_date = self.emp_strt_date
        emp_end_date = self.emp_end_date
        lm_start_date = self.lm_start_date
        lm_end_date = self.lm_end_date
        ulm_start_date = self.ulm_start_date
        ulm_end_date = self.ulm_end_date
        appraisal_update = self.env['hr.appraisal'].search(
            [('kw_ids', '=', self.id)])
        if len(appraisal_update) > 0:
            hr_appraisals = [emp.emp_id.id for emp in appraisal_update]
            for record in self.employee:
                survey_form = record.kw_survey_id.id
                for employee in record.employee_id:
                    training_score = self.calculate_training_score(self.year.fiscal_year_id,employee)
                    self.env.cr.execute(f" Select  CASE WHEN (q.type = 'textbox') THEN True  ELSE False END AS training from survey_question as q  join survey_page as p on q.page_id = p.id join survey_survey as s on s.id= p.survey_id where s.id = {survey_form}")
                    traning_dict = self._cr.dictfetchall()
                    training_present = any(item['training'] for item in traning_dict)
                    vals = {
                        'training_percentage':round(training_score[0]) if len(training_score)>0 and training_present == True else 0,
                        'planned_training_hours':training_score[1]  if len(training_score)>0 and training_score[1] != None  and training_present == True else '00:00:00',
                        'achieved_duration':training_score[2]  if len(training_score)>0 and training_score[2] != None   and training_present == True else '00:00:00',
                        'training_include':True if training_score[1] != None and training_score[1] != 0 and training_present == True else False,
                        'appraisal_year_rel': self.year.id,
                        'kw_ids': self.id,
                        'appraisal_year': self.year.assessment_period,
                        'emp_id': employee.id,
                        'appraisal_deadline': emp_end_date,
                        'app_period_from': start_date,
                        'hr_lm_start_date': lm_start_date,
                        'hr_lm_end_date': lm_end_date,
                        'hr_ulm_start_date': ulm_start_date,
                        'hr_ulm_end_date': ulm_end_date,
                        'hr_emp': True,
                        'emp_survey_id': survey_form,
                    }

                    if employee.parent_id:
                        vals['hr_manager_id'] = [(4, employee.parent_id.id)]
                        vals['hr_manager'] = True
                        vals['manager_survey_id'] = survey_form
                    if employee.parent_id.parent_id.id:
                        vals['hr_collaborator'] = True
                        vals['hr_collaborator_id'] = [
                            (4, employee.parent_id.parent_id.id)]
                        vals['collaborator_survey_id'] = survey_form
                    if employee.id not in hr_appraisals:
                        apr_create = self.env['hr.appraisal'].create(vals)
                        # if apr_create:
                        #     self.env.user.notify_success(message='Appraisal Updated successfully.')

                    else:
                        apr_date = self.env['hr.appraisal'].search(
                            [('emp_id', '=', employee.id), ('kw_ids', '=', self.id)])
                        if start_date != apr_date.app_period_from:
                            apr_date.write({
                                'app_period_from': start_date,
                            })
                        if emp_end_date != apr_date.appraisal_deadline:
                            apr_date.write({
                                'appraisal_deadline': emp_end_date,
                            })
                        if lm_start_date != apr_date.hr_lm_start_date:
                            apr_date.write({
                                'hr_lm_start_date': lm_start_date,
                            })
                        if lm_end_date != apr_date.hr_lm_end_date:
                            apr_date.write({
                                'hr_lm_end_date': lm_end_date,
                            })
                        if ulm_start_date != apr_date.hr_ulm_start_date:
                            apr_date.write({
                                'hr_ulm_start_date': ulm_start_date,
                            })
                        if ulm_end_date != apr_date.hr_ulm_end_date:
                            apr_date.write({
                                'hr_ulm_end_date': ulm_end_date,
                            })
                        if employee.parent_id.id != apr_date.hr_manager_id.id:
                            apr_date.write({
                                'hr_manager_id': (6, 0, [employee.parent_id.ids]),
                            })
                        if employee.parent_id.parent_id.id != apr_date.hr_collaborator_id.id:
                            apr_date.write({
                                'hr_collaborator_id': (6, 0, [employee.parent_id.parent_id.ids]),
                            })
                        hr_appraisals.remove(employee.id)
            for kw_id in hr_appraisals:
                self.env['hr.appraisal'].search([('emp_id', '=', kw_id)]).unlink()

        else:
            
            for record in self.employee:
                survey_form = record.kw_survey_id.id
                for employee in record.employee_id:
                    training_score = self.calculate_training_score(self.year.fiscal_year_id,employee)
                    self.env.cr.execute(f" Select  CASE WHEN (q.type = 'textbox') THEN True  ELSE False END AS training from survey_question as q  join survey_page as p on q.page_id = p.id join survey_survey as s on s.id= p.survey_id where s.id = {survey_form}")
                    
                    traning_dict = self._cr.dictfetchall()
                    training_present = any(item['training'] for item in traning_dict)
                    vals = {
                        'training_percentage':round(training_score[0]) if len(training_score)>0 and training_present == True else 0,
                        'planned_training_hours':training_score[1]  if len(training_score)>0 and training_score[1] != None  and training_present == True else '00:00:00',
                        'achieved_duration':training_score[2]  if len(training_score)>0 and training_score[2] != None   and training_present == True else '00:00:00',
                        'training_include':True if training_score[1] != None and training_score[1] != 0 and training_present == True else False,
                        'appraisal_year_rel': self.year.id,
                        'kw_ids': self.id,
                        'appraisal_year': self.year.assessment_period,
                        'emp_id': employee.id,
                        'appraisal_deadline': emp_end_date,
                        'app_period_from': start_date,
                        'hr_lm_start_date': lm_start_date,
                        'hr_lm_end_date': lm_end_date,
                        'hr_ulm_start_date': ulm_start_date,
                        'hr_ulm_end_date': ulm_end_date,
                        'hr_emp': True,
                        'emp_survey_id': survey_form,
                    }
                    if employee.parent_id:
                        vals['hr_manager_id'] = [(4, employee.parent_id.id)]
                        vals['hr_manager'] = True
                        vals['manager_survey_id'] = survey_form
                    if employee.parent_id.parent_id.id:
                        vals['hr_collaborator'] = True
                        vals['hr_collaborator_id'] = [(4, employee.parent_id.parent_id.id)]
                        vals['collaborator_survey_id'] = survey_form
                    hr_appr = self.env['hr.appraisal'].create(vals)
            if hr_appr:
                self.env.user.notify_success(message='Appraisal Updated successfully.')

        # State changing to self------------

        state = self.env['hr.appraisal'].search([('state', '=', 1)])
        state2 = self.env['hr.appraisal.stages'].search([('sequence', '=', 2)])
        for record_state in state:
            if record_state:
                record_state.state = state2
        return True

    


    @api.multi
    def action_update_appraisal(self):
        self.ensure_one()
        start_date = self.emp_strt_date
        emp_end_date = self.emp_end_date
        lm_start_date = self.lm_start_date
        lm_end_date = self.lm_end_date
        ulm_start_date = self.ulm_start_date
        ulm_end_date = self.ulm_end_date
        appraisal_update = self.env['hr.appraisal'].search([('kw_ids', '=', self.id)])
        if len(appraisal_update) > 0:
            hr_appraisals = [emp.emp_id.id for emp in appraisal_update]
            for record in self.employee:
                survey_form = record.kw_survey_id.id
                for employee in record.employee_id:
                    training_score = self.calculate_training_score(self.year.fiscal_year_id,employee)
                    
                    self.env.cr.execute(f" Select  CASE WHEN (q.type = 'textbox') THEN True  ELSE False END AS training from survey_question as q  join survey_page as p on q.page_id = p.id join survey_survey as s on s.id= p.survey_id where s.id = {survey_form}")
                    traning_dict = self._cr.dictfetchall()
                    training_present = any(item['training'] for item in traning_dict)
                    vals = {
                        'training_percentage':round(training_score[0]) if len(training_score)>0 and training_present == True else 0,
                        'planned_training_hours':training_score[1]  if len(training_score)>0 and training_score[1] != None  and training_present == True else '00:00:00',
                        'achieved_duration':training_score[2]  if len(training_score)>0 and training_score[2] != None   and training_present == True else '00:00:00',
                        'training_include':True if training_score[1] != None and training_present == True and training_score[1] != 0 else False,
                        'appraisal_year_rel': self.year.id,
                        'kw_ids': self.id,
                        'appraisal_year': self.year.assessment_period,
                        'emp_id': employee.id,
                        'appraisal_deadline': emp_end_date,
                        'app_period_from': start_date,
                        'hr_lm_start_date': lm_start_date,
                        'hr_lm_end_date': lm_end_date,
                        'hr_ulm_start_date': ulm_start_date,
                        'hr_ulm_end_date': ulm_end_date,
                        'hr_emp': True,
                        'emp_survey_id': survey_form,
                    }
                    if employee.parent_id:
                        vals['hr_manager_id'] = [(4, employee.parent_id.id, False)]
                        vals['hr_manager'] = True
                        vals['manager_survey_id'] = survey_form
                    if employee.parent_id.parent_id.id:
                        vals['hr_collaborator'] = True
                        vals['hr_collaborator_id'] = [
                            (4, employee.parent_id.parent_id.id, False)]
                        vals['collaborator_survey_id'] = survey_form
                    if employee.id not in hr_appraisals:
                        apr_create = self.env['hr.appraisal'].create(vals)
                        # if apr_create:
                        #     self.env.user.notify_success(message='Appraisal Updated successfully.')

                    else:
                        apr_date = self.env['hr.appraisal'].search(
                            ['&', ('emp_id', '=', employee.id), ('kw_ids', '=', self.id)])
                        if start_date != apr_date.app_period_from:
                            apr_date.write({
                                'app_period_from': start_date,
                            })
                        if emp_end_date != apr_date.appraisal_deadline:
                            apr_date.write({
                                'appraisal_deadline': emp_end_date,
                            })
                        if lm_start_date != apr_date.hr_lm_start_date:
                            apr_date.write({
                                'hr_lm_start_date': lm_start_date,
                            })
                        if lm_end_date != apr_date.hr_lm_end_date:
                            apr_date.write({
                                'hr_lm_end_date': lm_end_date,
                            })
                        if ulm_start_date != apr_date.hr_ulm_start_date:
                            apr_date.write({
                                'hr_ulm_start_date': ulm_start_date,
                            })
                        if ulm_end_date != apr_date.hr_ulm_end_date:
                            apr_date.write({
                                'hr_ulm_end_date': ulm_end_date,
                            })
                        if survey_form != apr_date.emp_survey_id.id:
                            apr_date.write({
                                'emp_survey_id': survey_form,
                                'manager_survey_id': survey_form,
                                'collaborator_survey_id': survey_form,
                            })
                        if employee.parent_id.id != apr_date.hr_manager_id.id or employee.parent_id.parent_id.id != apr_date.hr_collaborator_id.id:
                            if employee.parent_id.id:
                                apr_date.write({
                                    'hr_manager': True,
                                    'hr_manager_id': [(6, None, employee.parent_id.ids)],
                                })
                            elif not employee.parent_id.id:
                                apr_date.write({
                                    'hr_manager': False,
                                })
                            if employee.parent_id.parent_id.id:
                                apr_date.write({
                                    'hr_manager_id': [(6, None, employee.parent_id.ids)],
                                    'hr_collaborator': True,
                                    'hr_collaborator_id': [(6, None, employee.parent_id.parent_id.ids)],
                                })
                            elif not employee.parent_id.parent_id.id:
                                apr_date.write({
                                    'hr_manager_id': [(6, None, employee.parent_id.ids)],
                                    'hr_collaborator': False,
                                })
                        apr_date.training_percentage = round(training_score[0]) if len(training_score)>0 and training_present == True else 0
                        apr_date.planned_training_hours = training_score[1]  if len(training_score)>0 and training_score[1] != None  and training_present == True else '00:00:00'
                        apr_date.achieved_duration = training_score[2]  if len(training_score)>0 and training_score[2] != None   and training_present == True else '00:00:00'
                        apr_date.training_include = True if training_score[1] != None and training_present == True and training_score[1] != 0    else False
                        hr_appraisals.remove(employee.id)
            for kw_id in hr_appraisals:
                self.env['hr.appraisal'].search([('emp_id', '=', kw_id)]).unlink()
            self.env.user.notify_success(message='Appraisal Updated successfully.')
        else:
            for record in self.employee:
                survey_form = record.kw_survey_id.id
                for employee in record.employee_id:
                    training_score = self.calculate_training_score(self.year.fiscal_year_id,employee)
                    
                    self.env.cr.execute(f" Select  CASE WHEN (q.type = 'textbox') THEN True  ELSE False END AS training from survey_question as q  join survey_page as p on q.page_id = p.id join survey_survey as s on s.id= p.survey_id where s.id = {survey_form}")
                    traning_dict = self._cr.dictfetchall()
                    training_present = any(item['training'] for item in traning_dict)
                    vals = {
                        'training_percentage':round(training_score[0]) if len(training_score)>0 and training_present == True else 0,
                        'planned_training_hours':training_score[1]  if len(training_score)>0 and training_score[1] != None  and training_present == True else '00:00:00',
                        'achieved_duration':training_score[2]  if len(training_score)>0 and training_score[2] != None   and training_present == True else '00:00:00',
                        'training_include':True if training_score[1] != None and training_present == True and training_score[1] != 0  else False,
                        'appraisal_year_rel': self.year.id,
                        'kw_ids': self.id,
                        'appraisal_year': self.year.assessment_period,
                        'emp_id': employee.id,
                        'appraisal_deadline': emp_end_date,
                        'app_period_from': start_date,
                        'hr_lm_start_date': lm_start_date,
                        'hr_lm_end_date': lm_end_date,
                        'hr_ulm_start_date': ulm_start_date,
                        'hr_ulm_end_date': ulm_end_date,
                        'hr_emp': True,
                        'emp_survey_id': survey_form,
                    }

                    if employee.parent_id:
                        vals['hr_manager_id'] = [(4, employee.parent_id.id)]
                        vals['hr_manager'] = True
                        vals['manager_survey_id'] = survey_form
                    if employee.parent_id.parent_id.id:
                        vals['hr_collaborator'] = True
                        vals['hr_collaborator_id'] = [(4, employee.parent_id.parent_id.id)]
                        vals['collaborator_survey_id'] = survey_form
                    hr_appr = self.env['hr.appraisal'].create(vals)
            if hr_appr:
                self.env.user.notify_success(message='Appraisal Updated successfully.')

        # State changing to self------------

        emp_rec = self.env['hr.appraisal'].sudo().search([])
        for emp in emp_rec:
            emp_id = emp.emp_id.id
        resource_compare = self.env['resource.resource'].search([('user_id', '=', self.env.user.id)])
        # employees_find = self.env['hr.employee'].search([('resource_id','=',resource_compare.id)])
        employees = self.env['hr.employee'].search([('resource_id', '=', emp_id)])
        state = self.env['hr.appraisal'].search([('state', '=', 1)])
        state2 = self.env['hr.appraisal.stages'].search([('sequence', '=', 2)])
        for record_state in state:
            if record_state:
                record_state.state = state2
