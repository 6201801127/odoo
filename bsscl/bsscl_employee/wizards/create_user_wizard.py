
from odoo import api, fields, models,_


from odoo import api, fields, models,_


class ChangeRequestReject(models.TransientModel):
    _name = 'reject.change.request'
    _description = "Reject wizard"
    
    reject_reason = fields.Char(string="Reject Reason")

   
    def confirm_reject(self):
        context = dict(self._context)
        req_obj = self.env["change.request"]
        req_active_id = req_obj.browse(context.get("active_id"))
        req_active_id.status = 'reject'
        req_active_id.reason = self.reject_reason


    
        
        





