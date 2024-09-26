from ast import literal_eval
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MealExclusionWizard(models.TransientModel):
    _name = 'kw_canteen_meal_exclusion_wizard'
    _description = 'Meal Exclusion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reason = fields.Text(string="Reason")
    start_date = fields.Date(string="Starting Date")
    end_date = fields.Date(string="End Date")
    exclusion_type = fields.Selection([('temporary', 'Temporary'), ('permanent', 'Permanent')],default='temporary', required= True, string="Exclusion Type", tracking=True)
    regular_id = fields.Many2one(comodel_name="kw_canteen_regular_meal",string="Regular Meal ID",default=lambda self: self.env['kw_canteen_regular_meal'].search([('id','=',self.env.context.get('current_id'))]))
    
    @api.onchange('exclusion_type')
    def change_field_values(self):
        if self.exclusion_type:
            self.end_date = False
            self.reason =False
            self.start_date = False
            
    @api.multi
    def update_employee(self):
        rec = self.env['kw_canteen_regular_meal'].sudo().browse(self._context.get('current_id'))
        for record in self.regular_id.close_meal_ids:
            if self.start_date and self.end_date:
                if self.start_date >= record.start_date and self.end_date <= record.end_date or  self.end_date >= record.start_date and self.end_date <= record.end_date or  self.start_date >= record.start_date and self.start_date <= record.end_date or self.start_date <= record.start_date and self.end_date >= record.end_date or self.start_date >= record.start_date and self.end_date <= record.end_date :
                    raise ValidationError('Already applied for exclusion.')
                if self.start_date > self.end_date or self.regular_id.start_date > self.end_date:
                    raise ValidationError('End date should be greater than start date !')
        
        if self.exclusion_type == 'permanent':
            rec.write({
                    'end_date': self.end_date,
                    })
        elif self.exclusion_type == 'temporary':
            rec.write({'close_meal_ids': [[0,0,{
                            'exclusion_type':self.exclusion_type,
                            'reason': self.reason,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
                                 }]],
                        'apply_exclusion_boolean':True})

        param = self.env['ir.config_parameter'].sudo()
        canteen_autorities = literal_eval(param.get_param('kw_canteen.canteen'))
        if canteen_autorities:
            empls = self.env['hr.employee'].search([('id', 'in', canteen_autorities), ('active', '=', True)])
            # for record in self:
                # rec.write({'applied_by':self.env.user.employee_ids.id})
                # canteen_manager = self.env.ref('kw_canteen.canteen_manager_group').users
            mail_template = self.env.ref('kw_canteen.canteen_meal_exclusion_mail_template')
            email_to = ','.join(empls.mapped('work_email'))
            employee = rec.employee_id.name
            employee_code = rec.employee_id.emp_code
            email_from = rec.employee_id.work_email
            mail_template.with_context(emails=email_to,permanent_start_date = rec.start_date,employee=employee,email_from=email_from,employee_code=employee_code).send_mail(
                self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
