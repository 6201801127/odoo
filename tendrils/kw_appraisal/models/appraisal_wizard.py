import datetime
from email.policy import default
from xml.dom import ValidationErr
from dateutil import relativedelta
from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import exceptions
import locale


class appraisal_wizard(models.TransientModel):
    _name = 'appraisal_wizard'
    _description = 'Appraisal wizard'

    def _get_default_appraisal(self):
        return self.env['hr.appraisal'].browse(self.env.context.get('active_ids'))

    appr = fields.Many2many('hr.appraisal', readonly=1, default=_get_default_appraisal)
    appraisal_publish = fields.Selection([('publish_appraisal_result', 'Publish Appraisal Result Only')])

    @api.multi
    def action_publish_appraisal(self):
        rec = self.env['hr.appraisal.stages'].search([('sequence', '=', 6)])
        if not self.appraisal_publish:
            raise ValidationError("Please select a publish type.")
        else:
            for record in self:
                for states in record.appr:
                    states.state = rec.id
                    # ir_config_params = self.env['ir.config_parameter'].sudo()
                    # enable_mail = ir_config_params.get_param('kw_appraisal.enable_mail') or False
                    if self.appraisal_publish == 'increment_promotion':
                        current_ctc = '%.0f' % (states.employee_ctc * 12)
                        increment_per_month = '%.0f' % (states.final_increment * 12)
                        new_ctc_pm = '%.0f' % (states.final_ctc)
                        new_ctc_per_annum = '%.0f' % (states.final_ctc * 12)

                        job_role_id = self.env['hr.job.role'].search([('designations', 'in', [states.new_designation.id])],
                                                                    limit=1)
                        template = self.env.ref('kw_appraisal.kw_appraisal_result_email_template')
                        diff = relativedelta.relativedelta(datetime.datetime.today().date(), states.emp_id.date_of_joining)
                        employee_service_years = diff.years if diff.years > 0 else 1
                        template.with_context(
                            current_ctc=current_ctc,
                            increment_per_month=increment_per_month,
                            new_ctc_pm=new_ctc_pm,
                            new_ctc_per_annum=new_ctc_per_annum,
                            experience=f"{employee_service_years} {'years' if employee_service_years > 1 else 'year'}",
                            current_year=datetime.datetime.today().year,
                            jd=job_role_id.description).send_mail(states.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                        if states.new_designation:
                            states.emp_id.sudo().write({'job_id':states.new_designation.id})
                        if states.new_grade:
                            states.emp_id.sudo().write({'grade':states.new_grade.id})
                    else:
                        pass

            self.env.user.notify_info(message='Appraisal Published Sucessfully.')
        
