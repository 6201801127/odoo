from odoo import models,fields,api
from datetime import date, timedelta
import itertools
from dateutil import relativedelta
from odoo.exceptions import ValidationError , UserError
import math
from odoo.addons.kw_hr_leaves.models.kw_leave_type_config import CONFIG_GTYPE_MALE,CONFIG_GTYPE_FEMALE,CONFIG_GTYPE_BOTH,EMP_GENDER_TYPE_MALE,EMP_GENDER_TYPE_FEMALE,EMP_GENDER_TYPE_OTHER,NO_ENTITLEMENT

class EmployeeLeave(models.Model):
    _inherit = 'hr.employee'

    current_leave_state = fields.Selection(selection_add=[('hold', 'On Hold'),('forward', 'Forwarded')])
    
    @api.model
    def create(self,vals):
        """Allocate leave to midjoinee employees"""
        new_record = super(EmployeeLeave, self).create(vals)
        try:
            hr_leave_allocation = self.env['hr.leave.allocation']
            
            active_cycle        = self.env['kw_leave_cycle_master'].search([('branch_id','=',new_record.job_branch_id.id if new_record.job_branch_id else False),('cycle_id','!=',False),('active','=',True)],limit=1)
            
            if active_cycle and new_record.date_of_joining and new_record.employement_type and new_record.grade:
                    
                if active_cycle.from_date <= new_record.date_of_joining <= active_cycle.to_date:
                    leave_type  = self.env['hr.leave.type'].search([
                        ('allocation_type','in',['fixed','fixed_allocation']),
                        ('is_comp_off','=',False),
                        ])
                    
                    leave_type = leave_type.filtered(lambda res:new_record.employement_type.id in res.employement_type_ids.ids)
                    if leave_type:

                        for leave in leave_type:

                            gender = []
                            if new_record.gender and new_record.gender != EMP_GENDER_TYPE_OTHER:
                                gender = [CONFIG_GTYPE_MALE if new_record.gender == EMP_GENDER_TYPE_MALE else CONFIG_GTYPE_FEMALE,CONFIG_GTYPE_BOTH]
                            else:
                                gender = [CONFIG_GTYPE_BOTH]

                            config_record = self.env['kw_leave_type_config'].search([
                                ('leave_type_id','=',leave.id),
                                ('entitlement','!=',NO_ENTITLEMENT),
                                ('applicable_for','in',gender),
                                #('branch_id','=',new_record.job_branch_id.id or False)
                                ])
                            # print(config_record)
                            
                            config_record = config_record.filtered(lambda res: res.branch_id.id == new_record.job_branch_id.id) if config_record.filtered(lambda res: res.branch_id.id == new_record.job_branch_id.id) else config_record.filtered(lambda res: res.branch_id.id == False)
                            #print(config_record)
                            
                            if config_record:

                                grade_wise_leave_records = []

                                if config_record.grade_wise_leaves:

                                    grade_wise_leave_records = config_record.grade_wise_leaves.filtered(
                                        lambda entitlement: new_record.grade.id in entitlement.grade_ids.ids)
                                        
                                    if grade_wise_leave_records and new_record.emp_band:
                                        grade_wise_leave_records = grade_wise_leave_records.filtered(
                                        lambda entitlement: new_record.emp_band.id in entitlement.band_ids.ids if entitlement.band_ids else [False])

                                    if grade_wise_leave_records and grade_wise_leave_records.quantity > 0:
                                        
                                        total_count = 0

                                        if config_record.applicable_midjoinee and config_record.mid_joinee_rule:
                                            total_count = config_record._get_mid_joinee_count(grade_wise_leave_records.quantity,new_record.date_of_joining,active_cycle,True)
                                            
                                        else:
                                            total_count = config_record._get_mid_joinee_count(grade_wise_leave_records.quantity,new_record.date_of_joining,active_cycle,False)
                                            
                                        #print(total_count)
                                        if total_count > 0 :
                                            hr_leave_allocation.create({'employee_id':new_record.id,'holiday_status_id':leave.id,
                                            'name':leave.name +' fixed allocation by System on Employee Creation','state':'validate',
                                            'holiday_type':'employee','validity_start_date':active_cycle.from_date,
                                            'validity_end_date':active_cycle.to_date,
                                            'leave_cycle_id':active_cycle.id if active_cycle else False,'number_of_days':total_count,'cycle_period':active_cycle.cycle_period,'notes':leave.name +' fixed allocation by System on Employee Creation'})
                                        else:
                                            pass
                                        # print('--------------------------------------')
                                        # print({'employee_id':new_record.id,'holiday_status_id':leave.id,'name':leave.name +' fixed allocation by System on Employee Creation','state':'validate','holiday_type':'employee','validity_start_date':active_cycle.from_date,
                                        # 'validity_end_date':active_cycle.to_date,'leave_cycle_id':active_cycle.id if active_cycle else False,'number_of_days':total_count})
                                    
        except Exception as e:
            # print("Error in leave allocation during employee creation: ",e)
            pass
        #print(sdsd)
        return new_record

    """Reassign Leave with current cycle if employee details get changes"""

    def _get_cycle_details(self,branch):
        cycle_data = self.env['kw_leave_cycle_master'].search([('branch_id','=',branch),('cycle_id','!=',False),('active','=',True)],limit=1)
        return cycle_data
    
    def _get_config_record(self,leave_id,gender):
        config_data = self.env['kw_leave_type_config'].search([('leave_type_id','=',leave_id.id if leave_id else False),('entitlement','!=',NO_ENTITLEMENT),('applicable_for','in',gender)])
        return config_data

    def _get_branch_config(self,config_record,branch):
        config_data = config_record.filtered(lambda res: res.branch_id.id == branch) if config_record.filtered(lambda res: res.branch_id.id == branch) else config_record.filtered(lambda res: res.branch_id.id == False)
        return config_data

    def _get_grade_wise_config(self,config_record,grade):
        return config_record.grade_wise_leaves.filtered(lambda entitlement: grade in entitlement.grade_ids.ids)

    def _get_band_wise_config(self,grade_wise_leave_records,band):
        return grade_wise_leave_records.filtered(lambda entitlement: band in entitlement.band_ids.ids if entitlement.band_ids else [False])

    def _get_total_count(self,config_record,cycle,grade,band,l_type):
        grade_wise_entitles = []
        total_count = 0
        remain_months = 0

        if config_record.grade_wise_leaves:
            if grade:
                grade_wise_entitles = self._get_grade_wise_config(config_record,grade)
                    
            if grade_wise_entitles and band:
                grade_wise_entitles = self._get_band_wise_config(grade_wise_entitles,band)
            if grade_wise_entitles and grade_wise_entitles.quantity > 0:
                per_month   = grade_wise_entitles.quantity / 12

                if l_type == 'old':
                    remain_months   = (date.today().year - cycle.from_date.year) * 12 + (date.today().month - cycle.from_date.month)
                    # print("Old Completed Month ",remain_months)
                    total_count = (per_month * remain_months)
                elif l_type == 'new':
                    remain_months   = (cycle.to_date.year - date.today().year) * 12 + (cycle.to_date.month - date.today().month)
                    # print("New Remain Month ",remain_months)
                    total_count = per_month + (per_month * remain_months)
    
                if total_count > 0:
                    o_decimal = int(str('%.1f' % total_count).split('.')[1][0])
                    
                    total_count = round(total_count) if o_decimal != 5 else round(total_count,1)

        return total_count
    
    def _get_allocated_leaves(self,leave,cycle):
        hr_leave_allocation = self.env['hr.leave.allocation']
        filtered_data = hr_leave_allocation.search([('employee_id','=',self.id),('holiday_status_id','=',leave.id),
                                                    ('holiday_type','=','employee'),('cycle_period','=',cycle.cycle_period if cycle else False),
                                                    ('is_carried_forward','=',False)])
        return filtered_data

    @api.multi
    def write(self,vals):
        hr_leave_allocation = self.env['hr.leave.allocation']
        for record in self:
            try:
                if 'grade' in vals or 'emp_band' in vals:

                    old_active_cycle = record._get_cycle_details(record.job_branch_id.id) if record.job_branch_id else False
                    
                    branch      = False
                    emp_type    = False
                    grade       = False
                    band        = False

                    if 'job_branch_id' in vals:
                        branch = vals['job_branch_id']
                    elif record.job_branch_id:
                        branch = record.job_branch_id.id
                    
                    if 'employement_type' in vals:
                        emp_type = vals['employement_type']
                    elif record.employement_type:
                        emp_type = record.employement_type.id

                    if 'grade' in vals:
                        grade = vals['grade']
                    elif record.grade:
                        grade = record.grade.id
                    
                    if 'emp_band' in vals:
                        band = vals['emp_band']
                    elif record.grade:
                        band = record.emp_band.id
                    
                    updated_band    = False if 'emp_band' in vals and record.emp_band and vals['emp_band'] == record.emp_band.id else True
                    updated_grade   = False if 'grade' in vals and record.grade and vals['grade'] == record.grade.id else True
                    updated_branch  = False if 'job_branch_id' in vals and record.job_branch_id and vals['job_branch_id'] == record.job_branch_id.id else True
                    
                    if (branch and updated_branch) and (band and updated_band) and (updated_grade and grade) and emp_type and record.date_of_joining:
                        # print('comming')

                        active_cycle = record._get_cycle_details(branch)
                        # print(active_cycle)
                        if active_cycle:
                            # print("cycle exist")
                            if active_cycle.from_date <= date.today() <= active_cycle.to_date:
                                leave_type  = self.env['hr.leave.type'].search([
                                    ('allocation_type','in',['fixed','fixed_allocation']),
                                    ('is_comp_off','=',False),
                                    ])
                                
                                leave_type = leave_type.filtered(lambda res:emp_type in res.employement_type_ids.ids)
                                if leave_type:
                                    for leave in leave_type:
                                        # print ("------Leave Type = ",leave.name,"\n")
                                        
                                        gender = []
                                        if record.gender and record.gender != EMP_GENDER_TYPE_OTHER:
                                            gender = [CONFIG_GTYPE_MALE if record.gender == EMP_GENDER_TYPE_MALE else CONFIG_GTYPE_FEMALE,CONFIG_GTYPE_BOTH]
                                        else:
                                            gender = [CONFIG_GTYPE_BOTH]
                                        # print(gender)

                                        config_record = False
                                        branch_config_record = False
                                        branch_old_config_record = False
                                        
                                        total_count = 0
                                        old_total_count = 0
                                        # old_quantity = 0
                                        # new_quantity = 0

                                        """Leave allocations"""
                                        if leave:
                                            config_record = record._get_config_record(leave,gender)
                                            if config_record:
                                                """Current Branch wise config"""
                                                branch_config_record = record._get_branch_config(config_record,branch)
                                                
                                                if branch_config_record:
                                                    total_count = record._get_total_count(branch_config_record,active_cycle,grade,band,'new')
                                                    # print("Remaining Month total count ",total_count,"\n")
                                                    
                                                if record.job_branch_id:
                                                    """Last Branch wise config"""
                                                    branch_old_config_record = record._get_branch_config(config_record,record.job_branch_id.id)
                                                    
                                                    if branch_old_config_record and old_active_cycle:
                                                        old_total_count = record._get_total_count(branch_old_config_record,old_active_cycle,record.grade.id if record.grade else False,record.emp_band.id if record.emp_band else False,'old')
                                                        # print("Completed Month total count ",old_total_count)


                                            assigned_allocations = record._get_allocated_leaves(leave,old_active_cycle)
                                            allocated_total_quantity = sum([allocations.number_of_days for allocations in assigned_allocations])
                                            # print("Assigned allocations count ",allocated_total_quantity)
                                            total = (old_total_count + total_count) - allocated_total_quantity
                                            # print("Total inside assigned is : ",total)

                                            if total > 0 and branch_config_record:
                                                if assigned_allocations:
                                                    assigned_allocations.write({
                                                        'validity_start_date':active_cycle.from_date if active_cycle else False,
                                                        'validity_end_date':active_cycle.to_date if active_cycle else False,
                                                        'leave_cycle_id':active_cycle.id if active_cycle else False,'cycle_period':active_cycle.cycle_period
                                                    })

                                                hr_leave_allocation.create({'employee_id':record.id,'holiday_status_id':leave.id,
                                                'name':leave.name +' fixed allocation by System on Employee Updation','state':'validate',
                                                'holiday_type':'employee','validity_start_date':active_cycle.from_date,
                                                'validity_end_date':active_cycle.to_date,
                                                'leave_cycle_id':active_cycle.id if active_cycle else False,'number_of_days':total,'cycle_period':active_cycle.cycle_period,'notes':leave.name +' fixed allocation by System on Employee Updation'})
                else:
                    pass
            except Exception as e:
                # print("Error in leave allocation during employee updation : ",str(e))
                continue
        employee = super(EmployeeLeave, self).write(vals)
        # raise ValidationError("Ok")
        return employee