# -*- coding: utf-8 -*-
from odoo import models, fields, api

##send mail after creation , BY  T ketaki Debadarshini
class kw_hr_appraisal(models.Model):

    _inherit = 'hr.appraisal'
  

    
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
    
        result = super(kw_hr_appraisal, self).create(values)

        if result:
            try:
                mail_template    = self.env.ref('kw_appraisal.kw_employee_appraisal_draft_email_template')
                mail_template.send_mail(result.id,notif_layout="kwantify_theme.csm_mail_notification_light")

            except Exception as e:
                pass
    
        return result


class kw_appraisal_period(models.Model):

    _inherit = 'kw_appraisal'
  
    
    ##send mail to the employees acc to create Date
    @api.multi
    def action_send_mail_new_app(self):
        view_id = self.env.ref("kw_appraisal.send_mail_by_create_date_form").id
        action = {
            'name': 'Send Mail',
            'type': 'ir.actions.act_window',
            'res_model': 'send_mail_by_create_date',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action
    
    ##send mail to the employees of the appraisal period
    @api.multi
    def action_send_mail(self):
        for record in self:
            try:
                appraisal_recs = self.env['hr.appraisal'].search([('kw_ids', '=', record.id)])

                if appraisal_recs:
                    mail_template    = self.env.ref('kw_appraisal.kw_employee_appraisal_draft_email_template')
                    for appraisal_rec in appraisal_recs:
                        mail_template.send_mail(appraisal_rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            except Exception as e:
                pass

        return True






    