from odoo import api, fields, models,_
from datetime import datetime
import re
from odoo.exceptions import ValidationError, UserError



class ApproveWizard(models.TransientModel):
    _name = 'approve_wizard'
    _description = "Approve wizard"
    
    remark = fields.Char(string="Remark",size=50)
   
    def confirm_reason(self):
        active_id   = self.env['bsscl_employee_apply_attendance'].browse(self.env.context.get('active_ids'))
        diff_hour = active_id.check_out_datetime - active_id.check_in_datetime
        work_hour = diff_hour.total_seconds()
        active_id.update({
            'state':'3',
            'authority_remark':self.remark
        })
        self.env['hr.attendance'].sudo().create({
            'employee_id':active_id.employee_id.id,
            'check_in':active_id.check_in_datetime,
            'check_out':active_id.check_out_datetime,
            'worked_hours':work_hour
        })

    @api.constrains('remark')
    def validate_remark(self):
        for record in self:
            if record.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z0-9\s]*$',str(record.remark)):
                raise ValidationError("remark should start from an alphabet and should be alphanumeric")       
        
    

class RejectWizard(models.TransientModel):
    _name = 'reject_wizard'
    _description = "Reject wizard"
    
    remark = fields.Char(string="Remark",size=50)
   
    def reject_reason(self):
        active_id   = self.env['bsscl_employee_apply_attendance'].browse(self.env.context.get('active_ids'))
        active_id.update({
            'state':'5',
            'authority_remark':self.remark
        })

    @api.constrains('remark')
    def validate_remark(self):
        for record in self:
            if record.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z0-9\s]*$',str(record.remark)):
                raise ValidationError("remark should start from an alphabet and should be alphanumeric")       

class CancelWizard(models.TransientModel):
    _name = 'cancel_wizard'
    _description = "Cancel wizard"
    
    remark = fields.Char(string="Remark",size=50)
   
    def cancel_reason(self):
        active_id   = self.env['bsscl_employee_apply_attendance'].browse(self.env.context.get('active_ids'))
        active_id.update({
            'state':'6',
            'authority_remark':self.remark
        })

    @api.constrains('remark')
    def validate_remark(self):
        for record in self:
            if record.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z0-9\s]*$',str(record.remark)):
                raise ValidationError("remark should start from an alphabet and should be alphanumeric")
        

