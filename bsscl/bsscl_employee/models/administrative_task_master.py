# *******************************************************************************************************************
#  File Name             :   administrative_task_master.py
#  Description           :   This is a mster model which is used to keep all administrative task type record 
#  Created by            :   Ajay Kumar Ravidas
#  Created On            :   20-02-2023
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************
from odoo import fields, models, api ,_ 

class AdministrativeTaskMaster(models.Model):
    _name ="administrative.task.master"
    _description ="Administrative Task Master Model"

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have Administrative task type with the same name ! / आपके पास समान नाम वाला प्रशासनिक कार्य प्रकार नहीं हो सकता!'),
        ('ref_code_uniq', 'UNIQUE (ref_code)',  'You can not have Administrative task code with the same name ! / आपके पास समान नाम वाला प्रशासनिक कार्य कोड नहीं हो सकता है')
    ]
    name = fields.Char(string="Name / नाम")
    ref_code = fields.Char('Code / कोड')


# *********************************************** Duty type master model********************************************* 
class DutyTypeMaster(models.Model):
    _name ="duty.type.master"
    _description ="Duty Type Master Model"

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have duty type with the same name ! / आपके पास समान नाम वाला कर्तव्य प्रकार नहीं हो सकता!')
    ]
    name = fields.Char(string="Name / नाम")
# ************************************************* End ************************************************************* 

class AdministrativeTaskDetails(models.Model):
    _name = "administrative.task.details"
    _description = "Administrative Task Details"

    task_type_id = fields.Many2one(comodel_name="administrative.task.master")

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
    promotion_bool = fields.Boolean(striong='Task Type Promotion')
    trf_bool = fields.Boolean(striong='Task Type Transfer')
    spcl_duty_bool = fields.Boolean(striong='Task Type Transfer')
    other_task_bool = fields.Boolean(striong='Task Type Others')
    confirm_button_bool = fields.Boolean(striong='Confirm Call', default=False)


    def print_pdf(self):
        action_print_pdf = self.env.ref('bsscl_employee.tranfer_employee_detail_id')
        return action_print_pdf.report_action(self)