# *******************************************************************************************************************
#  File Name             :   employee_administrative_task_wiz.py
#  Description           :   This is a transient model which is used to promotion of an employee whose employement
#  type is regular in BSSCL 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   10-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************

from odoo import models, fields ,_ ,api
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta


class EmployeeAdministrativeTask(models.TransientModel):
    _name = "administrative.task"
    _description ="Employee Administrative model"
    _rec_name = 'task_type_id'

    task_type_id = fields.Many2one(comodel_name="administrative.task.master", default=lambda self: self.env['administrative.task.master'].search([('ref_code','=','PR')]), string="Task Type / कार्य प्रकार")

    # **************************************Promotion Details ************************************************
    mode_of_promotion = fields.Selection([('test_period','Probation'),
                                            ('contract','Contract'),
                                            ('deputation','Deputation'),
                                            ('employment','Regular')],string="Stage / अवस्था")
    new_desig_id = fields.Many2one(comodel_name="hr.job", string="New Designation-post / नवीन पद-पद")
    personal_concern_file_no = fields.Char(string="Personal/Concern File No./ व्यक्तिगत/चिंता फाइल सं.")
    promotion_date = fields.Date(string="Joining/Promotion Date / ज्वाइनिंग/पदोन्नति दिनांक")
    salary_id = fields.Many2one(comodel_name="hr.payroll.structure", string="Salary Type / वेतन प्रकार")
    order_no = fields.Char(string="Order No. / आदेश संख्या")
    order_date = fields.Date(string="Order Date / आर्डर की तारीख")
    remarks = fields.Text(string="Remarks / टिप्पणियां")
    employee_id =fields.Many2one('hr.employee')
    #*************************************** *****End ***********************************************************

    #******************************************Transfer Dtails **************************************************
    current_work_location = fields.Char(string="Work Location / वर्तमान कार्य स्थान")
    transfer_work_location = fields.Char(string="Transfer Work Location / स्थानांतरण कार्य स्थान")
    transfer_joining_date = fields.Date(string="Transfer Joining Date / स्थानांतरण कार्यग्रहण तिथि")
    attachement = fields.Binary(string="Upload Document / दस्तावेज़ अपलोड करें") 
    #************************************************ End *******************************************************

    #**************************************** Special duty assignment Details ***********************************
    duty_id = fields.Many2one(comodel_name="duty.type.master", string="Type of Duty / कर्तव्य का प्रकार")
    from_date = fields.Date(string="From Date / की तिथि से")
    to_date = fields.Date(string="To Date / तारीख तक")
    assign_by_id = fields.Many2one(comodel_name="hr.employee",string="Assigned By / द्वारा सौंपा")
    # ****************************************************** End ************************************************

    #******************************* Boolean fields for compute method *****************************************
    promotion_bool = fields.Boolean(striong='Task Type Promotion',compute='_compute_promotion_bool')
    trf_bool = fields.Boolean(striong='Task Type Transfer', compute='_compute_trf_bool')
    spcl_duty_bool = fields.Boolean(striong='Task Type Transfer', compute='_compute_spcl_duty_bool')
    other_task_bool = fields.Boolean(striong='Task Type Others', compute='_compute_other_task_bool')
    confirm_button_bool = fields.Boolean(striong='Confirm Call', default=False)
    # ******************************** End ***************************************************************

    #*********************************** Onchange methods ************************************************
    @api.onchange('task_type_id')
    def _onchange_task_type_id(self):
        if self.task_type_id.ref_code == 'OT':
            self.order_date = date.today()
    #************************************************* End ***********************************************

    # ***************************compute method **********************************************************
    @api.depends('task_type_id')
    def _compute_promotion_bool(self):
        for rec in self:
            if rec.task_type_id.ref_code == "PR":
                rec.promotion_bool = True
            else:
                rec.promotion_bool = False

    @api.depends('task_type_id')
    def _compute_trf_bool(self):
        for rec in self:
            if rec.task_type_id.ref_code == "TR":
                rec.trf_bool = True
            else:
                rec.trf_bool = False

    @api.depends('task_type_id')
    def _compute_spcl_duty_bool(self):
        for rec in self:
            if rec.task_type_id.ref_code == "SDA":
                rec.spcl_duty_bool = True
            else:
                rec.spcl_duty_bool = False

    @api.depends('task_type_id')
    def _compute_other_task_bool(self):
        for rec in self:
            if rec.task_type_id.ref_code == "OT":
                rec.other_task_bool = True
            else:
                rec.other_task_bool = False
    
    # def print_pdf(self):
    #     action_print_pdf = self.env.ref('bsscl_employee.tranfer_employee_detail_id')
    #     return action_print_pdf.report_action(self)

    # ************************************* End **********************************************************

    #********************************** Method call by confirm button ************************************************
    def action_confirm(self):
        self.confirm_button_bool = True
        if self.task_type_id.ref_code == 'PR':
            promotion_ids = []
            active_id = self._context.get('active_id')
            act_id = self.env['hr.employee'].browse(int(active_id))
            contract_id = self.env['hr.contract'].search([('employee_id','=',act_id.id),('state','=','open')],limit=1)
            if contract_id:
                contract_id.update({'state':'close','date_end': self.promotion_date})
            promotion_ids.append([0,0, {
                'task_type_id': self.task_type_id.id,
                'mode_of_promotion': self.mode_of_promotion,
                'new_desig_id': self.new_desig_id.id,
                'personal_concern_file_no': self.personal_concern_file_no,
                'promotion_date': self.promotion_date,
                'salary_id': self.salary_id.id,
                'current_work_location':self.current_work_location,
                'order_no': self.order_no,
                'order_date':self.order_date,
                'remarks': self.remarks,
                'promotion_bool': self.promotion_bool,
                'confirm_button_bool': True
                
            }])
            act_id.write({
                'administrative_task_ids': promotion_ids,
                'job_id' : self.new_desig_id.id,
                'state' :self.mode_of_promotion

                })

            if act_id.employee_type == 'regular':
                self.env['hr.contract'].create(
                    {
                        'state': 'open',
                        'name': act_id.name,
                        'employee_id': act_id.id,
                        'department_id': act_id.department_id.id,
                        'job_id': self.new_desig_id.id,
                        'struct_id': self.salary_id.id,
                        'date_start': self.promotion_date,
                        'resource_calendar_id':act_id.resource_calendar_id.id,
                        'mode_of_promotion':self.mode_of_promotion,
                        'employee_type':act_id.employee_type,
                        'wage':10000,
                        'hra': 10000*12/100,
                        'da': 10000*8/100,
                        'medical_allowance': 10000*5/100,
                        'meal_allowance': 10000*5/100,
                        'other_allowance': 10000*70/100,
                    }
                )
        elif self.task_type_id.ref_code == 'TR':
            transfer_ids = []
            active_id = self._context.get('active_id')
            act_id = self.env['hr.employee'].browse(int(active_id))
            transfer_ids.append([0,0, {
                'task_type_id':self.task_type_id.id,
                'current_work_location': self.current_work_location,
                'transfer_work_location': self.transfer_work_location,
                'transfer_joining_date': self.transfer_joining_date,
                'order_date': self.order_date,
                'order_no': self.order_no,
                'remarks':self.remarks,
                'attachement': self.attachement,
                'trf_bool': self.trf_bool,
                'confirm_button_bool': True
                
            }])
            act_id.write({
                'administrative_task_ids': transfer_ids,
                'work_location' : self.transfer_work_location,
                })


        elif self.task_type_id.ref_code == 'SDA':
            spl_duty_ids = []
            active_id = self._context.get('active_id')
            act_id = self.env['hr.employee'].browse(int(active_id))
            spl_duty_ids.append([0,0, {
                'task_type_id':self.task_type_id.id,
                'duty_id': self.duty_id.id,
                'order_date': self.order_date,
                'order_no': self.order_no,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'current_work_location':self.current_work_location,
                'assign_by_id': self.assign_by_id.id,
                'remarks': self.remarks,
                'spcl_duty_bool': self.spcl_duty_bool,
                'confirm_button_bool': True
            }])
            act_id.write({
                'administrative_task_ids': spl_duty_ids,
                })
        elif self.task_type_id.ref_code == 'OT':
            others_ids = []
            active_id = self._context.get('active_id')
            act_id = self.env['hr.employee'].browse(int(active_id))
            others_ids.append([0,0, {
                'task_type_id':self.task_type_id.id,
                'order_date': self.order_date,
                'current_work_location':self.current_work_location,
                'assign_by_id': self.assign_by_id.id,
                'remarks': self.remarks,
                'other_task_bool': self.other_task_bool,
                'confirm_button_bool': True
            }])
            act_id.write({
                'administrative_task_ids': others_ids,
                })
        else:
            pass
    
    # ************************************* End **********************************************************
