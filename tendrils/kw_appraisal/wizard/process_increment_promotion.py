from odoo import models, fields, api,SUPERUSER_ID
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import math


class AppraisalIncrementPro(models.TransientModel):
    _name           = 'process_increment_promotion'
    _description    = "Appraisal Increment Promotion"
    
    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    company_id = fields.Many2one('res.company',string="Company")
    country_id = fields.Char(string='Country',related = 'company_id.country_id.name')


    def action_process_increment_promotion(self):
        if self.period_id:
            cr = self._cr

            cr.execute(f"SELECT id FROM hr_employee WHERE enable_payroll='yes' AND   active = true and employement_type IN (SELECT id FROM kwemp_employment_type WHERE code NOT IN ('CE', 'O') ) and company_id = {self.company_id.id}")
            employee_ids = [row[0] for row in cr.fetchall()]


            for employee_id in employee_ids:
                cr.execute("SELECT id FROM hr_appraisal WHERE emp_id=%s and appraisal_year_rel = %s", (employee_id,self.period_id.id))
                appraisal_id = cr.fetchone()
                cr.execute("SELECT grade,level,department_id,division FROM hr_employee WHERE id=%s", (employee_id,))
                grade = cr.fetchone()
                if grade[0] != None and grade[2] != None:
                    cr.execute("SELECT wage FROM hr_contract WHERE state='open' and  employee_id=%s", (employee_id,))
                    wage = cr.fetchone()
                    increment_value = 0
                    if wage and wage[0]!= None and wage[0] >0:
                        increment_rec = self.env['increment_master'].sudo().search([('period_id','=',self.period_id.id)])
                        increment_percentage = increment_rec.filtered(lambda x: grade[0] in x.grade_ids.ids and x.department.id == grade[2])
                        per_increment = 0
                        for inc in increment_percentage:
                            if grade[3] and inc.division.id == grade[3]:
                                per_increment = inc.per_increment
                                increment_value = wage[0] * per_increment / 100
                                inc.write({
                                    'process_bol':True
                                })
                            elif not grade[3] and not inc.division:
                                per_increment = inc.per_increment
                                increment_value = wage[0] * per_increment / 100
                                inc.write({
                                    'process_bol':True
                                })
                            elif grade[3] and grade[3] not in inc.division.ids:
                                if not inc.division:
                                    per_increment = inc.per_increment 
                                    increment_value = wage[0] * per_increment / 100
                                    inc.write({
                                        'process_bol':True
                                    })

                        cr.execute("SELECT primary_skill_id FROM resource_skill_data WHERE employee_id=%s", (employee_id,))
                        primary_skill = cr.fetchone()

                        cr.execute("SELECT date_of_joining FROM hr_employee WHERE id=%s", (employee_id,))
                        date_of_joining = cr.fetchone()

                        if date_of_joining and date_of_joining[0] < fields.Date.from_string(self.period_id.fiscal_year_id.date_start):
                            increment_effective_date = self.period_id.fiscal_year_id.date_start + relativedelta(years=1)
                        else:
                            increment_effective_date = date_of_joining[0] + relativedelta(days= 1,years=1)

                        vals = {
                            'add_in_appraisal': 'yes' if appraisal_id else 'no',
                            'appraisal_id': appraisal_id if appraisal_id else None,
                            'employee_id': employee_id,
                            'period_id': self.period_id.id,
                            'grade': grade[0] if grade else None,
                            'job_id': None,  
                            'department_id': None,  
                            'date_of_joining': date_of_joining[0],
                            'division': None,  
                            'emp_band': None, 
                            'budget_type': None,  
                            'level': None,  
                            'state':  None,
                            'actual_increment_amount': increment_value,
                            'actual_increment_percentage': per_increment,
                            'current_ctc': wage[0],
                            'actual_ctc': increment_value + wage[0],
                            'status': 'draft',
                            'hod_id': None, 
                            'actual_increment_percentage_2': per_increment,
                            'gender': None, 
                            'sbu_master_id': None,
                            'primary_skill': primary_skill if primary_skill else None,
                            'increment_effective_date': increment_effective_date,
                            'increment_month':increment_effective_date.month
                        }

                        cr.execute("""
                            SELECT e.job_id, e.department_id, d.manager_id, e.division, e.emp_band, e.budget_type, e.level, e.gender, e.sbu_master_id,e.last_working_day
                            FROM hr_employee AS e
                            LEFT JOIN hr_department AS d ON e.department_id = d.id
                            WHERE e.id = %s
                        """, (employee_id,))
                        result = cr.fetchone()
                        

                        if result:
                            job_id, department_id, hod_id, division, emp_band, budget_type, level, gender, sbu_master_id,last_working_day = result
                        else:
                            job_id, department_id, hod_id, division, emp_band, budget_type, level, gender, sbu_master_id,last_working_day = (None, None, None, None, None, None, None, None, None,None)
                        
                        vals['job_id'] = job_id if job_id else None
                        vals['department_id'] = department_id if department_id else None
                        vals['hod_id'] = hod_id if hod_id else None
                        vals['division'] = division if division else None
                        vals['emp_band'] = emp_band if emp_band else None
                        vals['budget_type'] = budget_type if budget_type else None
                        vals['level'] = level if level else None
                        vals['gender'] = gender if gender else None
                        vals['sbu_master_id'] = sbu_master_id if sbu_master_id else None
                        vals['last_working_day'] = last_working_day if last_working_day else None
                        # print("vals['last_working_day']=======================",vals['last_working_day'],employee_id)

                        query_to_select_iaa = f"SELECT user_id FROM appraisal_btn_user_rel AS user_rel JOIN appraisal_btn_department_rel AS dept_rel ON user_rel.config_id = dept_rel.config_id join kw_appraisal_btn_config_master b on b.id = user_rel.config_id WHERE dept_rel.dept_id = {department_id} and type='hod'"
                        cr.execute(query_to_select_iaa)
                        user_config_dict = cr.dictfetchall()
                        iaas_record = [d['user_id'] for d in user_config_dict]
                         
                        cr.execute("SELECT id FROM shared_increment_promotion WHERE employee_id=%s AND period_id=%s", (employee_id, self.period_id.id))
                        check_promotion = cr.fetchone()
                        if not check_promotion:
                            cr.execute("INSERT INTO shared_increment_promotion (add_in_appraisal, appraisal_id, employee_id, period_id, grade_id, job_id, department_id, date_of_joining, division, emp_band, budget_type, level, state, actual_increment_amount, actual_increment_percentage, current_ctc, actual_ctc, status, hod_id, actual_increment_percentage_2, gender, sbu_master_id, primary_skill_id, increment_effective_date,increment_month,last_working_day) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)", (vals['add_in_appraisal'], vals['appraisal_id'], vals['employee_id'], vals['period_id'], vals['grade'], vals['job_id'], vals['department_id'], vals['date_of_joining'], vals['division'], vals['emp_band'], vals['budget_type'], vals['level'], vals['state'], vals['actual_increment_amount'], vals['actual_increment_percentage'], vals['current_ctc'], vals['actual_ctc'], vals['status'], vals['hod_id'], vals['actual_increment_percentage_2'], vals['gender'], vals['sbu_master_id'], vals['primary_skill'], vals['increment_effective_date'],vals['increment_month'],vals['last_working_day']))
                            cr.execute(f"select id from shared_increment_promotion where employee_id= {employee_id} and period_id = {self.period_id.id}")
                            promotion = cr.fetchone()
                            inc = self.env['shared_increment_promotion'].sudo().browse(promotion[0])
                            records_to_link = [(6, 0, iaas_record)]
                            inc.write({'iaas_ids': records_to_link})
                            cr.execute(f"UPDATE shared_increment_promotion SET applied_eos = True WHERE period_id = {self.period_id.id} and employee_id IN (SELECT applicant_id FROM kw_resignation WHERE (state NOT IN ('reject', 'cancel')) AND (applicant_id ={employee_id}) LIMIT 1)")
                        else:
                            cr.execute("UPDATE shared_increment_promotion SET add_in_appraisal=%s,appraisal_id=%s, state=%s, hod_id=%s, increment_effective_date=%s , last_working_day = %s , current_ctc = %s, actual_ctc = %s WHERE employee_id=%s AND period_id=%s", (vals['add_in_appraisal'],  vals['appraisal_id'],vals['state'], vals['hod_id'], vals['increment_effective_date'],vals['last_working_day'],vals['current_ctc'], vals['actual_ctc'], vals['employee_id'], self.period_id.id))
                            inc = self.env['shared_increment_promotion'].sudo().browse(check_promotion[0])
                            records_to_link = [(6, 0, iaas_record)]
                            inc.write({'iaas_ids': records_to_link})
                            cr.execute(f"UPDATE shared_increment_promotion SET applied_eos = True WHERE period_id = {self.period_id.id} and employee_id IN (SELECT applicant_id FROM kw_resignation WHERE (state NOT IN ('reject', 'cancel')) AND (applicant_id ={employee_id}) LIMIT 1)")
                            # cr.execute(f"UPDATE shared_increment_promotion SET applied_eos = True WHERE employee_id IN (SELECT applicant_id FROM kw_resignation WHERE state NOT IN ('reject', 'cancel'))")
                            # cr.execute(f"UPDATE shared_increment_promotion SET last_working_day = (SELECT b.last_working_day FROM hr_employee b WHERE b.id = shared_increment_promotion.employee_id)")
                    else:
                        raise ValidationError(f"Kindly update {self.env['hr.employee'].browse(employee_id).name}'s current CTC in the contract.")
                else:
                    raise ValidationError(f"Kindly update the department, grade  for {self.env['hr.employee'].browse(employee_id).name}")
            # cr.execute("UPDATE kw_appraisal_btn_config_master set active = false WHERE type = 'manager'")
            
            
        #     return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
    def update_dept_desg(self):
        all_increments = self.env['shared_increment_promotion'].sudo().search([('period_id','=',self.period_id.id)])
        if all_increments:
            filtered_rec = all_increments.filtered(lambda x: x.department_id.id != x.employee_id.department_id.id or x.division.id != x.employee_id.division.id)
            for record in filtered_rec:
                record.department_id =  record.employee_id.department_id.id
                record.division =  record.employee_id.division.id
            # for rec in all_increments:
            #     if rec.appraisal_id:
            #         rec.total_final_score= rec.appraisal_id.total_score
            #         rec.proposed_increment =  rec.appraisal_id.increment_percentage

    def update_ctc(self):
        self._cr.execute(f"SELECT id FROM shared_increment_promotion where period_id = {self.period_id.id}")
        increments = [row[0] for row in self._cr.fetchall()]
        for inc in increments:
            self._cr.execute(f"UPDATE shared_increment_promotion SET  actual_ctc = current_ctc + actual_increment_amount,  hod_actual_ctc = current_ctc + hod_amount_auto ,chro_actual_ctc =  current_ctc + chro_amount_auto WHERE id = {inc}")
            
    def update_changed_by_iaa(self):
        self._cr.execute(f"SELECT id FROM shared_increment_promotion where period_id = {self.period_id.id}")
        increments = [row[0] for row in self._cr.fetchall()]
        for inc in increments:
            self._cr.execute(f"""
    UPDATE shared_increment_promotion 
    SET changed_by_iaa = 
        CASE 
            WHEN hod_inc_auto > 0 AND actual_increment_percentage != hod_inc_auto THEN True 
            ELSE False 
        END 
    WHERE id = {inc}
""")

            
            
class AppraisalIncrementPromotion(models.TransientModel):
    _name           = 'update_resigned_last_day'
    _description    = "Appraisal Increment Promotion Updation"
    
    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    increment_ids = fields.Char(compute='compute_increment_ids')
    id_from = fields.Integer()
    id_to = fields.Integer()
    joining_date = fields.Date()


    @api.depends('period_id')
    def compute_increment_ids(self):
        if self.period_id:
            self._cr.execute(f"SELECT id FROM shared_increment_promotion WHERE period_id = {self.period_id.id} order by id asc")
            result = self._cr.fetchall()
            self.increment_ids = tuple(id_[0] for id_ in result) if result else False

    def delet_record(self):
        if self.joining_date and self.period_id:
            self._cr.execute(f"DELETE FROM shared_increment_promotion WHERE period_id = {self.period_id.id}  and  date_of_joining >= '{self.joining_date}'")
    
    def update_resigned_details(self):
        if self.period_id and self.id_from >0  and self.id_to > 0:
           self._cr.execute(f"""
    UPDATE shared_increment_promotion 
    SET applied_eos = True 
    FROM kw_resignation 
    WHERE 
        shared_increment_promotion.employee_id = kw_resignation.applicant_id 
        AND kw_resignation.state NOT IN ('reject', 'cancel') 
        AND shared_increment_promotion.id BETWEEN {self.id_from} AND {self.id_to} 
        AND shared_increment_promotion.period_id = {self.period_id.id}
""")

        self._cr.execute(f"""
    UPDATE shared_increment_promotion 
    SET last_working_day = (
        SELECT 
            CASE 
                WHEN b.last_working_day IS NOT NULL THEN b.last_working_day 
                ELSE shared_increment_promotion.last_working_day 
            END
        FROM hr_employee b 
        WHERE b.id = shared_increment_promotion.employee_id
    ) 
    WHERE 
        id BETWEEN {self.id_from} AND {self.id_to} 
        AND period_id = {self.period_id.id}
""")
    
        
    
             
    def update_changed_by_iaa(self):
        self._cr.execute(f"SELECT id FROM shared_increment_promotion where period_id = {self.period_id.id}")
        increments = [row[0] for row in self._cr.fetchall()]
        for inc in increments:
            self._cr.execute(f"""
    UPDATE shared_increment_promotion 
    SET changed_by_iaa = 
        CASE 
            WHEN hod_inc_auto > 0 AND actual_increment_percentage != hod_inc_auto THEN True 
            ELSE False 
        END 
    WHERE id = {inc}
""")

    
