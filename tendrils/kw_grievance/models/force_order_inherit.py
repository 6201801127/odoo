from odoo import models, fields, api

class GrievanceFO(models.Model):

    _inherit = 'kw.force.order'
    

    grievance_id = fields.Many2one('kw.grievance',string="Grievance",domain="[('state','=','approve')]")



    @api.model
    def create(self, vals):
        res = super(GrievanceFO, self).create(vals)
        if res.grievance_id:
            res.grievance_id.state = 'closed'
            cmd_list = []
            users = self.env['res.users'].sudo().search([])
            branch_commandant = users.filtered(lambda user: user.has_group('kw_grievance.griev_commandant')==True)
            branch_commandant_user = branch_commandant.filtered(lambda x:res.grievance_id.employee_id.current_office_id.id in x.branch_ids.ids)
            if branch_commandant_user:
                for rec in branch_commandant_user:
                    if rec.employee_ids.work_email:
                        cmd_list.append(rec.employee_ids.work_email)
            email_cc = ','.join(cmd_list)
            template = self.env.ref('kw_grievance.email_forceorder_template')
            template.with_context(email_cc=email_cc).send_mail(res.id)
        self.env.user.notify_success("Notification sent Successfully.")
        return res