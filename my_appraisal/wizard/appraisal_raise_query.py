from odoo import models, fields,_ 

class AppraisalRaiseQuery(models.TransientModel):
    _name="appraisal.raisequery"

    query_remarks = fields.Text(string="Query Remarks")

    def submit_query_action(self):
        active_id = self._context.get('active_id')
        act_id = self.env['employee.appraisal'].browse(int(active_id))
        act_id.query_remarks = self.query_remarks
        act_id.write({'state': 'raise_query'})
        for line in act_id.kpia_ids:
            line.write({'state': 'raise_query'})
        for line1 in act_id.kpia_ids1:
            line1.write({'state': 'raise_query'})
        for line2 in act_id.kpia_ids2:
            line2.write({'state': 'raise_query'})