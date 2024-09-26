from odoo import api, fields, models, tools, _
from datetime import date, datetime
import calendar




class MetricRemark(models.TransientModel):
    _name = "metric_remark"
    _description = "Project Performer Metrices Remark"
    
    
    remark = fields.Text()
    
    
    def reject_btn(self):
        if self.env.context.get('current_id'):
            project = self.env['kw_project_performer_metrics'].sudo().search([('id','=', self.env.context.get('current_id'))])
            if project:
                project.write({
                    'state':'reject',
                    'updated_on':date.today(),
                    'updated_by':self.env.user.employee_ids.id,
                    'remark':self.remark
                })
                template = self.env.ref('kw_project_performer_metrics.kw_project_performer_metrics_email_template')
                mail_to = project.employee_id.work_email
                name = project.employee_id.name
                month = calendar.month_name[int(project.month)]
                template.with_context(email_to=mail_to,state='Rejected',name=name,month=month).send_mail(project.id,notif_layout="kwantify_theme.csm_mail_notification_light")

