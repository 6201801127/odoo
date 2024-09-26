from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class StarlightGenaralConfiguration(models.Model):
    _name = "kw_starlight_general_configuration"
    _description = "Starlight General Configuration"
    _rec_name = 'name'

    name = fields.Char(string='Congratulation Mail From')
    cc_notify = fields.Many2many('hr.employee', 'kw_starlight_general_configuration_rnr_employee_rel', 'employee_id',
                                 'res_id', string='CC Notify',
                                 help='Select the employee to be added in the cc of all emails')
    nomination_start_date = fields.Date(string='Nomination Start Date',
                                        help="Select Date Range on which Nomination window will be available and Reminder email will sent")
    nomination_end_date = fields.Date(string='Nomination End Date',
                                      help="Select Date Range on which Nomination window will be available and Reminder email will sent")
    review_start_date = fields.Date(string='Review Start Date',
                                    help="Select Date on which Review window will be available and Reminder email will sent")
    review_end_Date = fields.Date(string='Review End Date',
                                  help="Select Date on which Review window will be available and Reminder email will sent")
    show_publish_option_date = fields.Date(string='Publish Start Date',
                                           help="Select Date after which publish Option will be available.")
    show_publish_option_end_date = fields.Date(string='Publish End Date',
                                           help="Select till which publish Option will be available.")
    congratulation_reminder = fields.Date(string='Congratulation Reminder',
                                          help="Select Date on which Congratulation Reminder email will sent")
    congratulation_mail_from = fields.Char(string='Congratulation Mail From',
                                           help='Add email from whom Congratulation email will be sent')
    congratulation_mail_to = fields.Char(string='Congratulation Mail To',
                                         help='Add email To whom Congratulation email will be sent')

    @api.multi
    def redirect_starlight_configuration(self):
        form_view_id = self.env.ref('kw_reward_and_recognition.kw_starlight_general_configuration_view_form').id
        last_config_id = self.env['kw_starlight_general_configuration'].sudo().search([], order='id desc', limit=1)
        return {
            'name': 'General Settings',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_starlight_general_configuration',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'self',
            'res_id': last_config_id.id,
            'context': {'create': False, 'delete': False},
            'flags': {'mode': 'edit', },
        }
