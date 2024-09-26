import string
from odoo import api, fields, models, _

class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'
    _description = 'Grievance  Rejection Wizard'

    rejection_reason = fields.Text(string="Reverted Reason")


    def reject_application(self):
        context = dict(self._context)
        intObj = self.env["bsscl.grievance"]
        int_details = intObj.browse(context.get("active_id"))
        print("int_details=========================",int_details.employee_id.name)
        email_to=int_details.employee_id.work_email 
        email_cc=int_details.employee_id.parent_id.work_email
        rejected_by=int_details.env.user.name
        gri_no=int_details.grievance_code

        # template = self.env.ref('bsap_grievance.bsap_grievance_rejection_mail')
        # template.with_context(email_to=email_to,email_cc=email_cc,to_name=int_details.employee_id.name,gr_no=gri_no,remark=self.rejection_reason,rejected_by=rejected_by).send_mail(
        # int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        int_details.state = 'reset'


class RejectWizardAction(models.TransientModel):
    _name = 'reject.wizard.action'
    _description = 'Grievance  Rejection Wizard'

    reject_reason_griev = fields.Char(string="Reject Reason")


    def reject_reason(self):
        context = dict(self._context)
        intObj = self.env["bsscl.grievance"]
        int_details = intObj.browse(context.get("active_id"))
        print("int_details=========================",int_details.employee_id.name)
        
        # rejected_by=int_details.env.user.name
        # gri_no=int_details.grievance_code
        int_details.state = 'reject'
        int_details.rej_reas = self.reject_reason_griev