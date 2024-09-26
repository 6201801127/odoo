from odoo import models, fields, api


class kw_adv_apply_petty_cash_wizard(models.TransientModel):
    _name = 'kw_advance_apply_petty_cash_wizard'
    _description = 'Apply Petty Cash Wizard'

    petty_cash_record_id = fields.Many2one('kw_advance_apply_petty_cash', string='ref')
    forwardto_id = fields.Many2one('hr.employee', string="Employee", required=True, default=lambda self: self.petty_cash_record_id.action_to_be_taken_by)
    remark = fields.Text(string="remark", required=True)
    
    
    def petty_cash_fwd_take_action_btn(self):
        if self.petty_cash_record_id.state in ['applied','forward']:
            self.petty_cash_record_id.write({
                'state': 'forward',
                'remark': self.remark,
                'action_to_be_taken_by': self.forwardto_id.id,
                'forwarded_by': self.env.user.employee_ids.name,
                })
            # self.env.user.notify_success("Forwarded successfully")
            """#Log"""
            record = self.env['kw_advance_log_petty_cash'].create({
                'from_user_id':self._uid,
                'forwarded_to_user_id':self.forwardto_id.user_id.id,
                'remark':self.remark
                })
            
            forwardto_email = self.forwardto_id.work_email
            forwardto_name = self.forwardto_id.name
            mail_context = 'Forwarded'
            template_id = self.env.ref('kw_advance_claim.kw_petty_cash_forward_mail_template')
            template_id.with_context(status=mail_context,mail=forwardto_email,name=forwardto_name).send_mail(self.petty_cash_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            user_template_id = self.env.ref('kw_advance_claim.kw_petty_cash_user_forward_mail_template')
            user_template_id.with_context(
                status=mail_context,mail=self.petty_cash_record_id.user_emp_id.work_email,name=self.petty_cash_record_id.user_emp_id.name,fname=self.forwardto_id.name).send_mail(self.petty_cash_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        return {'type': 'ir.actions.act_window_close'}
    
    @api.onchange('forwardto_id')
    def get_forwardto_id(self):
        fwd_lst = []
        login_user_id = self.env.user.employee_ids.id
        ra_group = self.env.ref('bsscl_employee.group_hr_ra')
        ra_employee_ids = ra_group.users.mapped('employee_ids') or False
        if ra_employee_ids:
            fwd_lst = ra_employee_ids.ids
            # for rec in ra_employee_ids:
            #     fwd_lst.append(rec.id)
        fwd_lst.remove(login_user_id)
        return {'domain': {'forwardto_id': [('id', 'in', fwd_lst)]}}





