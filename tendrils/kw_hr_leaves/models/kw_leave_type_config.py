from odoo import models, fields, api
import datetime,calendar
from odoo.exceptions import ValidationError
from datetime import datetime as dttime ,date, timedelta
from dateutil.relativedelta import relativedelta

EMP_GENDER_TYPE_MALE,EMP_GENDER_TYPE_FEMALE,EMP_GENDER_TYPE_OTHER = 'male','female','other'
CONFIG_GTYPE_MALE,CONFIG_GTYPE_FEMALE,CONFIG_GTYPE_BOTH = 'm','f','b'

MONTHLY_ENTITLEMENT, YEARLY_ENTITLEMENT, QUATERLY_ENTITLEMENT, NO_ENTITLEMENT = 'months','years','quater','none'

from odoo.addons.kw_hr_leaves.models.hr_leave_type import LEAVE_TYPE_MT

class KwLeaveTypeConfig(models.Model):
    _name           = 'kw_leave_type_config'
    _description    = "Leave type configuration"
    _rec_name       = "leave_type_id"

   
    branch_id       = fields.Many2one('kw_res_branch', string="Branch")
    leave_type_id   = fields.Many2one('hr.leave.type', string="Leave Type", required=True)

    absent_deduction         = fields.Boolean(string='Absent Deduction')
    exclude_holiday          = fields.Boolean(string='Exclude Holiday')
    applicable_for           = fields.Selection([(CONFIG_GTYPE_MALE, 'Male'),
                                       (CONFIG_GTYPE_FEMALE, 'Female'),
                                       (CONFIG_GTYPE_BOTH, 'Both')],
                                      string='Applicable For' , default =CONFIG_GTYPE_BOTH)

    monthly_credit          = fields.Boolean(string="Monthly Credit")
    entitlement              = fields.Selection([(YEARLY_ENTITLEMENT, 'Yearly'),(NO_ENTITLEMENT, 'None')],string='Entitlement' , default =YEARLY_ENTITLEMENT)

    avail_leave_within_cycle = fields.Boolean(string='Leave Availability Restricted for Cycle')

    description              = fields.Text(string='Description')
    is_restricted            = fields.Boolean(string='Is Restricted')    
    # is_restricted            = fields.Boolean(string='Is Restricted')
    
    monthly_allowed_leave    = fields.Float(string='Maximum Leave in a Month(in days)') 
    leave_cycle_applicable   = fields.Boolean(string='Leave Cycle Applicable',default=True)
    validity_days            = fields.Integer(string='Lapse After (in days)')
    service_days             = fields.Integer(string='Applicable after completion of Service Days') 
    applicable_midjoinee     = fields.Boolean(string='Applicable for Mid Joinee')
    mid_joinee_rule          = fields.Many2one('kw_credit_rule_config', string="Mid Joinee Rule")
    grade_wise_leaves        = fields.One2many('kw_grade_wise_leave_entitlements', 'leave_config_id')

    _sql_constraints         = [('branch_leave_uniq', 'unique (branch_id,leave_type_id)','This leave type already exist under same branch!')]

    @api.constrains('branch_id','leave_type_id')
    def leave_uniq(self):
        for record in self:
            if not record.branch_id:
                leave_config = self.env['kw_leave_type_config'].search([('branch_id','=',False),('leave_type_id','=',record.leave_type_id.id)])- self
                if leave_config:
                    raise ValidationError("This leave type already exist.")

    @api.model
    def _get_month_name_list(self):
        months_choices = []
        for i in range(1, 13):
            months_choices.append((str(i), datetime.date(2008, i, 1).strftime('%B')))
        return months_choices
    
    @api.onchange('leave_cycle_applicable')
    def onchange_leave_cycle_applicable(self):
        if self.leave_cycle_applicable:
            self.validity_days       = 0
        
    
    @api.onchange('applicable_midjoinee')
    def onchange_applicable_midjoinee(self):
        if self.applicable_midjoinee:
            self.mid_joinee_rule   = None

    @api.multi
    def load_all_grades(self):
        grade_records = self.env['kwemp_grade'].search([])
        for record in self:
            for grade in grade_records:
               
                if record.grade_wise_leaves and grade in record.grade_wise_leaves.mapped('grade_id'):
                    pass
                else:
                   record.grade_wise_leaves = [(0, 0, {'grade_id': grade.id, 'quantity': 0})]

    @api.multi
    def get_leave_type_config_wise_employees(self,leave_cycle):
        """Method to allocate leave as per the configuration"""
        #self.ensure_one()
        # print('branch configs -------')
        #hr_employee                      = self.env['hr.employee']
        all_emp_records_to_config         = self.env['hr.employee']
        curr_date                         = dttime.today().date()
        hr_leave_allocation               = self.env['hr.leave.allocation']
        #branch_records                   = self.env['kw_res_branch']

        #get branchwise leave type configs
        leave_config_rec              = self.filtered(lambda rec: rec.branch_id and rec.branch_id.id==leave_cycle.branch_id.id and rec.entitlement != NO_ENTITLEMENT)
        # print(leave_config_rec)
        if not leave_config_rec:
            leave_config_rec          = self.filtered(lambda rec: not rec.branch_id.id and rec.entitlement != NO_ENTITLEMENT)

        all_emp_records_to_config     = self.env['hr.employee'].search([('job_branch_id','=',leave_cycle.branch_id.id)])
        # print(leave_config_rec)
        
        #branch_records                   = branch_specific_configs.mapped('branch_id')
        # print(branch_records)
        #default_config_setting           = self-branch_specific_configs
        
        #print(bvnvbnvbn)
        # for all leave configuration records in the leave cycle
        if all_emp_records_to_config and leave_config_rec :
            leave_config_rec.ensure_one()
            #for leave_config_rec in leave_config_records:
            leave_allocations_data  = []
            # print('leave type----',leave_config_rec.leave_type_id.name,leave_config_rec.branch_id)                
            
            #if leave_config_rec.entitlement and leave_config_rec.entitlement not in [NO_ENTITLEMENT]:

            ## all the operations will be based on the branch record sets
            # if leave_config_rec.branch_id:
            #     all_emp_records_to_config = hr_employee.search([('job_branch_id','=',leave_config_rec.branch_id.id)])
            # else:
            #     emp_domain = [('job_branch_id','not in',branch_records.ids)] if branch_records else []
            #     all_emp_records_to_config = hr_employee.search(emp_domain)
                
            ##allocate only in case of leave cycle is applicable
            emp_records_to_assign     = all_emp_records_to_config                
            
            if leave_config_rec.leave_type_id.employement_type_ids:
                emp_records_to_assign = emp_records_to_assign.filtered(lambda rec: rec.employement_type.id in leave_config_rec.leave_type_id.employement_type_ids.ids)

            
            """start applying the leave allocation as per the leave configuration"""
            # Check if gender specific rule applicable 
            if leave_config_rec.applicable_for and leave_config_rec.applicable_for != CONFIG_GTYPE_BOTH:

                emp_records_to_assign = emp_records_to_assign.filtered(lambda rec: rec.gender  == (EMP_GENDER_TYPE_MALE if leave_config_rec.applicable_for == CONFIG_GTYPE_MALE else EMP_GENDER_TYPE_FEMALE))
                    
            # print(asas)

            """check if allocation config exists / loop through each employee to assign"""
            if leave_config_rec.grade_wise_leaves:
                
                for grade_wise_entitlement in leave_config_rec.grade_wise_leaves:

                    emp_recs        = False
                    emp_recs        = emp_records_to_assign.filtered(lambda rec: rec.grade in grade_wise_entitlement.grade_ids)
                    # print(grade_wise_entitlement.grade_ids)
                    #print('grade wise records ---',emp_recs)
                    if grade_wise_entitlement.band_ids:
                        emp_recs    = emp_recs.filtered(lambda rec: rec.grade in grade_wise_entitlement.grade_ids and rec.emp_band in grade_wise_entitlement.band_ids)
                    
                    # lapse_day lapse_month curr_month curr_day
                    for employee in emp_recs:
                        if grade_wise_entitlement.quantity>0:
                          
                            try:                                
                                # print('-----------------',leave_config_rec.leave_type_id.name +' fixed allocation by System',leave_cycle.branch_id.name)  
                            
                                credit_dates,lapse_date    = leave_config_rec.get_leave_config_wise_credit_lapse_days(leave_cycle) 
                                ##if the setting is set for other than no entitlement and leave entitlement date matches
                                if curr_date >= leave_cycle.from_date and curr_date <= leave_cycle.to_date  : #and curr_date == credit_dates    
                                    #print(credit_dates,lapse_date)
                                    # print('##################################')                                            
                                    #leave_allocations_data.append({'employee_id':employee.id,'holiday_status_id':leave_config_rec.leave_type_id.id,'name':leave_config_rec.leave_type_id.name +' fixed allocation by System','state':'validate','holiday_type':'employee','validity_start_date':curr_date,'validity_end_date':lapse_date,'leave_cycle_id':leave_cycle.id,'number_of_days':grade_wise_entitlement.quantity})

                                    #self.env['hr.leave.allocation'].search([('employee_id','=',employee.id)])
                                    no_allocation = 0
                                    if leave_config_rec.leave_type_id.leave_code.lower() == LEAVE_TYPE_MT.lower():
                                        if self.env['hr.leave'].search([('employee_id','=',employee.id),('state', '=', 'validate'),
                                        '|', '|',
                                        '&', ('request_date_from', '<=', credit_dates), ('request_date_to', '>=', credit_dates),
                                        '|',
                                        '&', ('request_date_from', '<=', lapse_date), ('request_date_to', '>=', lapse_date),
                                        '&', ('request_date_from', '<=', credit_dates), ('request_date_to', '>=', lapse_date),
                                        '|',
                                        '&', ('request_date_from', '>=', credit_dates), ('request_date_from', '<=', lapse_date),
                                        '&', ('request_date_to', '>=', credit_dates), ('request_date_to', '<=', lapse_date)]):

                                            no_allocation =1
                                            
                                    if no_allocation ==0:
                                        existing_rec = self.env['hr.leave.allocation'].search([('employee_id','=',employee.id),('holiday_status_id','=',leave_config_rec.leave_type_id.id),('leave_cycle_id','=',leave_cycle.id)])
                                        # print('existingrec ---------')
                                        # print(existing_rec)
                                        ##get quantity as per the mid joinee rule
                                        mid_joinee_rule_required = True if employee.date_of_joining and employee.date_of_joining > credit_dates else False 
                                        total_count              = leave_config_rec._get_mid_joinee_count(grade_wise_entitlement.quantity,employee.date_of_joining,leave_cycle,mid_joinee_rule_required)
                                        month_number = datetime.date.today().month
                                        nxt_mnth = datetime.date.today().replace(day=28) + datetime.timedelta(days=4)
                                        res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)

                                        if leave_config_rec.monthly_credit:
                                            if not len(existing_rec) == month_number: #and res.day == datetime.date.today().day
                                                total_count = total_count / 12
                                                hr_leave_allocation.create({'employee_id':employee.id,'holiday_status_id':leave_config_rec.leave_type_id.id,'name':leave_config_rec.leave_type_id.name +' fixed allocation by System','notes':'Fixed allocation by System as per leave policy','state':'validate','holiday_type':'employee','validity_start_date':credit_dates,'validity_end_date':lapse_date,'leave_cycle_id':leave_cycle.id,'number_of_days':total_count,'cycle_period':leave_cycle.cycle_period})
                                        else:
                                            if not existing_rec: 
                                                hr_leave_allocation.create({'employee_id':employee.id,'holiday_status_id':leave_config_rec.leave_type_id.id,'name':leave_config_rec.leave_type_id.name +' fixed allocation by System','notes':'Fixed allocation by System as per leave policy','state':'validate','holiday_type':'employee','validity_start_date':credit_dates,'validity_end_date':lapse_date,'leave_cycle_id':leave_cycle.id,'number_of_days':total_count,'cycle_period':leave_cycle.cycle_period})
                                            else:
                                                for ext_leave_rec in existing_rec:
                                                    if not ext_leave_rec.is_carried_forward or ext_leave_rec.is_carried_forward is None:
                                                        existing_rec.write({'employee_id':employee.id,'holiday_status_id':leave_config_rec.leave_type_id.id,'name':leave_config_rec.leave_type_id.name +' fixed allocation by System','notes':'Fixed allocation by System as per leave policy','state':'validate','holiday_type':'employee','validity_start_date':credit_dates,'validity_end_date':lapse_date,'leave_cycle_id':leave_cycle.id,'number_of_days':total_count,'cycle_period':leave_cycle.cycle_period})

                            except Exception as e:
                                continue

                # if leave_allocations_data:
                #     print(leave_allocations_data)
                            
        
        return True
    
    @api.multi
    def get_leave_config_wise_credit_lapse_days(self,active_leave_cycle):
        """ @params  : active leave cycle
            @returns : list of credit days as per the entitlement config and lapse date
        """

        self.ensure_one()

        if self.leave_type_id.is_comp_off:
            validity_days       = self.leave_allocation_request_id.validity_days if self.leave_allocation_request_id.validity_days and self.leave_allocation_request_id.validity_days >0 else 90 

            cycle_start_date    = date.today()
            cycle_end_date      = cycle_start_date+ timedelta(days=validity_days)
        else:
            cycle_start_date        = active_leave_cycle.from_date
            cycle_end_date          = active_leave_cycle.to_date

        # credit_date,lapse_date  = self.get_leave_credit_lapse_days(active_leave_cycle)

        # delta       = relativedelta(days=0)
        # credit_days = []
        # if self.entitlement == QUATERLY_ENTITLEMENT:
        #     delta   = relativedelta(months=3)
        # elif self.entitlement == MONTHLY_ENTITLEMENT:  
        #     delta   = relativedelta(months=1)
        # elif self.entitlement == YEARLY_ENTITLEMENT:  
        #     delta   = relativedelta(years=1)

        # start_date  = credit_date
        # credit_days.append(start_date)
        # while start_date <=cycle_end_date:
        #     # print(start_date+ delta)
        #     start_date = start_date+ delta
        #     if start_date<= cycle_end_date:
        #         credit_days.append(start_date)
        # print('credit days ----------')
        # print(credit_days)
        return [cycle_start_date,cycle_end_date]

    @api.multi
    def get_leave_credit_lapse_days(self,active_leave_cycle):
        """ @params : active leave cycle
            @returns : credit date and lapse date
        """
        self.ensure_one()
        cycle_start_date    = active_leave_cycle.from_date
        cycle_end_date      = active_leave_cycle.to_date
        # print(cycle_start_date,cycle_end_date)
        
        if cycle_start_date.year != cycle_end_date.year:
            # print(self.credit_day,self.credit_month)
            credit_date_1  = cycle_start_date.replace(day=int(self.credit_day),month=int(self.credit_month))
            credit_date_2  = cycle_end_date.replace(day=int(self.credit_day),month=int(self.credit_month))

            if credit_date_1 and credit_date_1 >= cycle_start_date and credit_date_1 <= cycle_end_date:
                credit_date    = credit_date_1
            elif credit_date_2 and credit_date_2 >= cycle_start_date and credit_date_2 <= cycle_end_date:
                credit_date    = credit_date_2
            else:
                credit_date    = cycle_start_date
        else:
            credit_date     = cycle_start_date.replace(day=int(self.credit_day),month=int(self.credit_month))     

        # print("credit date -- ",credit_date)
        if self.validity_ends_with and self.validity_ends_with == 'months':
            lapse_date    = credit_date.replace(day=int(self.lapse_day),month=int(self.lapse_month))

            if lapse_date < credit_date:
                lapse_date = lapse_date.replace(year=lapse_date.year+1)
            
            # print(lapse_date)
        else:
            lapse_date      = credit_date + timedelta(days=self.validity_days)            


        return [credit_date,lapse_date]
    
    def allocation_expire_date(self,employee_id,holiday_status_id):

        leave_config_wbranch = self.env['kw_leave_type_config'].search([('branch_id','=',employee_id.user_id.branch_id.id),('leave_type_id','=',holiday_status_id.id)])
        if leave_config_wbranch:
            config= leave_config_wbranch
        else:
            leave_config = self.env['kw_leave_type_config'].search([('branch_id','=',False),('leave_type_id','=',holiday_status_id.id)])
            if leave_config:
                config = leave_config
        if config.leave_cycle_applicable:
            lapse_date = date(year=date.today().year,month=int(config.lapse_month),day=int(config.lapse_day))
            if date.today() <= lapse_date:
                expire_date = lapse_date
            else :
                expire_date = date(year=date.today().year+1,month=int(config.lapse_month),day=int(config.lapse_day))

        else:
            expire_date = date.today() + timedelta(days=config.validity_days)
        return expire_date

    @api.constrains('entitlement','grade_wise_leaves')
    def _validate_grade_wise_leaves(self):
        for record in self:
            if record.entitlement != NO_ENTITLEMENT:
                if not record.grade_wise_leaves:
                    raise ValidationError(f"Entitlement list should not be blank.")
                else:
                    for config in record.grade_wise_leaves:
                        grades          = config.mapped('grade_ids')
                        existing_grades =  record.grade_wise_leaves.filtered(lambda res: res.grade_ids in grades) - config
                        duplicate_band  = existing_grades.mapped('band_ids') & config.band_ids
                        if duplicate_band:
                            raise ValidationError("Duplicate band or grade configuration exists !")  
                        
    @api.model
    def _get_mid_joinee_count(self,quantity,joining_date,cycle,mid_joinee_required):        
        """
            Method to get the entitlement count according to mid joinee rule
            Created By : Nikunja Maharana
            Created On : 02-Mar-2021  
        """  
        total_count         = 0        

        if mid_joinee_required and self.applicable_midjoinee and self.mid_joinee_rule:
            remain_months   = (cycle.to_date.year - joining_date.year) * 12 + (cycle.to_date.month - joining_date.month)
            per_month       = quantity / 12

            rule_id         = self.mid_joinee_rule.rule_ids.filtered(lambda rule:rule.from_day <= joining_date.day <= rule.to_day)
            total_count     = (per_month / 100 * rule_id.percentage if rule_id else 0) + (per_month * remain_months)
        else:
            total_count     = quantity
        
        if not self.monthly_credit and total_count > 0:
            decimal         = int(str('%.1f' % total_count).split('.')[1][0])            
            total_count     = round(total_count) if decimal != 5 else round(total_count,1)

        return total_count

class KwGradewiseLeaveEntitlements(models.Model):

    _name           = 'kw_grade_wise_leave_entitlements'
    _description    = "Grade wise leave entitlement"
    _rec_name       = "leave_config_id"    


    leave_config_id = fields.Many2one('kw_leave_type_config', string="Leave Type Config", required=True)
    grade_ids       = fields.Many2many('kwemp_grade_master',string="Grades", required=True)
    band_ids        = fields.Many2many('kwemp_band_master',string="Bands")
    quantity        = fields.Float(string='Quantity',required=True)
