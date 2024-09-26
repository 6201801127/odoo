from odoo import models, fields, api


class kw_apply_salary_advance_wizard(models.TransientModel):
    _name = 'kw_apply_salary_advance_wizard'
    _description = 'Apply Salary Advance Wizard'

    forwardto_id = fields.Many2one('hr.employee', string="Forward To",required=True)
    remark = fields.Text(string="remark",required=True)
    salary_advance_record_id = fields.Many2one('kw_advance_apply_salary_advance',string="Ref")
    
    @api.multi
    def sal_adv_fwd_take_action_btn(self):
        if self.salary_advance_record_id.state in ['applied','forward']:
            self.salary_advance_record_id.write({
                'state': 'forward',
                'remark': self.remark,
                'action_to_be_taken_by': self.forwardto_id.id,
                'forwarded_by': self.env.user.employee_ids.id,
                })

            self.env.user.notify_success("Forwarded successfully")
            #Log
            record = self.env['kw_advance_log_salary_advance'].create({
                'from_user_id':self._uid,
                'forwarded_to_user_id':self.forwardto_id.user_id.id,
                'remark':self.remark
                })
            
            forwardto_email = self.forwardto_id.work_email
            forwardto_name = self.forwardto_id.name
            mail_context = 'Forwarded'
            template_id = self.env.ref('kw_advance_claim.kw_salary_advance_forward_mail_template')
            template_id.with_context(status=mail_context,mail=forwardto_email,name=forwardto_name).send_mail(self.salary_advance_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            user_template_id = self.env.ref('kw_advance_claim.kw_salary_advance_forward_user_mail_template')
            user_template_id.with_context(
                status=mail_context,
                mail=self.salary_advance_record_id.employee_id.work_email,
                name=self.salary_advance_record_id.employee_id.name,
                fname=self.forwardto_id.name).send_mail(self.salary_advance_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        # return {'type': 'ir.actions.act_window_close'}
        action_id = self.env.ref('kw_advance_claim.kw_apply_salary_advance_action').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_advance_apply_salary_advance&view_type=list',
                    'target': 'self',
                }
    
    @api.onchange('forwardto_id')
    def get_forwardto_id(self):
        fwd_lst = []
        login_user_id = self.env.user.employee_ids.id
        ra_group = self.env.ref('kw_employee.group_hr_ra')
        ra_employee_ids = ra_group.users.mapped('employee_ids') or False
        if ra_employee_ids:
            for rec in ra_employee_ids:
                fwd_lst.append(rec.id)
        fwd_lst.remove(login_user_id)
        return {'domain': {'forwardto_id': [('id', 'in', fwd_lst)]}}
