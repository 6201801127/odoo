from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError


class add_health_insurance_dependencies(models.Model):
    _name = 'add_health_insurance_dependencies'
    _rec_name = 'employee_id'
    _description = "Request for Dependants"


    health_insurance_id = fields.Integer(readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Name",readonly=True)
    year_id = fields.Many2one('account.fiscalyear', string="Financial Year",readonly=True)
    relationship_id = fields.Many2one('kwmaster_relationship_name',domain="[('is_insure_covered','=',True),('name','in',['Son','Daughter','Wife','Husband'])]",required=True)
    department = fields.Char('Department')
    dependant_name = fields.Char(required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')], required=True)
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    state = fields.Selection([('Requested', 'Requested'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],default='Requested')


    @api.model
    def create(self,vals):
        if vals.get('relationship_id') and vals.get('year_id') and vals.get('employee_id'):
            relationship_name = self.env['kwmaster_relationship_name'].browse(vals['relationship_id']).name
            if relationship_name in ['Wife', 'Husband']:
                existing_record = self.search([('employee_id', '=', vals['employee_id']),('year_id', '=', vals['year_id']),('relationship_id', '=', vals['relationship_id'])])
                if existing_record:
                    raise ValidationError("Cannot add wife or husband twice for the same financial year.")


        record = super(add_health_insurance_dependencies, self).create(vals)
        template = self.env.ref('payroll_inherit.dependant_approval_request_mail_template')
        email_from = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else ''
        applied_user = self.env.user.employee_ids.name
        hlth_ins_mngrs = self.env.ref('payroll_inherit.payroll_insurance_group').users
        email_to = ','.join(hlth_ins_mngrs.mapped("email")) if hlth_ins_mngrs else ''
        if email_to:
            template.with_context(email_to=email_to, email_from=email_from,applied_user=applied_user).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        return record


    @api.onchange('relationship_id')
    def get_context_values(self):
        for rec in self:
            rec.health_insurance_id = self.env.context.get('health_insurance_id')
            rec.employee_id = self.env.context.get('employee_id')
            rec.year_id = self.env.context.get('year_id')
            rec.department = self.env.context.get('department')


    def approve_dependencies(self):
        for rec in self:
            # self.env['family_details'].create({'family_details_id':rec.health_insurance_id,
            #                                           'relationship_id':rec.relationship_id.id,
            #                                           'gender':rec.gender,
            #                                           'dependant_id':rec.dependant_name,
            #                                           'date_of_birth':rec.date_of_birth})
            self.env.cr.execute(f"INSERT INTO family_details (family_details_id, relationship_id, gender, dependant_id, date_of_birth) VALUES ({rec.health_insurance_id}, {rec.relationship_id.id}, '{rec.gender}', '{rec.dependant_name}', '{rec.date_of_birth}')")

            rec.state = 'Approved'

            template = self.env.ref('payroll_inherit.dependant_approval_rejection_mail_template')
            email_from = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else ''
            email_to = rec.employee_id.work_email if rec.employee_id.work_email else []
            applied_user = rec.employee_id.name if rec.employee_id.name else 'User'
            template.with_context(email_to=email_to, email_from=email_from,applied_user=applied_user,state=rec.state).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")



    def reject_dependencies(self):
        for rec in self:
            rec.state = 'Rejected'

            template = self.env.ref('payroll_inherit.dependant_approval_rejection_mail_template')
            email_from = self.env.user.employee_ids.work_email if self.env.user.employee_ids.work_email else ''
            email_to = rec.employee_id.work_email if rec.employee_id.work_email else []
            applied_user = rec.employee_id.name if rec.employee_id.name else 'User'
            hlth_ins_mngrs = self.env.ref('payroll_inherit.payroll_insurance_group').users
            hlth_ins_mngrs_name = ','.join(hlth_ins_mngrs.mapped("name")) if hlth_ins_mngrs else 'Insurance Managers'
            template.with_context(email_to=email_to, email_from=email_from,applied_user=applied_user,hlth_ins_mngrs_name=hlth_ins_mngrs_name,state=rec.state).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")

