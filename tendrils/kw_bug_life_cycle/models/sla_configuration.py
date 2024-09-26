from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SLAConfig(models.Model):
    _name = 'sla_config'
    _description = 'sla_config'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    question = fields.Selection(selection=[('yes', 'Yes'),
                                           ('no', 'No'),
                                           ('NA', 'NA')], string="""Is it a Showstopper (Is this defect stopping another bunch of test scenario or cases to be executed) ? 
                                            Are you in Pre-UAT or UAT phase ?
                                            Is the application is going to be LIVE very soon (within a week) ?  
                                            DEMO to client in next couple of days ?""")
    sla_config_time_ids = fields.One2many('sla_config_stages', 'sla_config_id', string="Working Hour Yes")
    sla_config_time_no_ids = fields.One2many('sla_config_stages_no', 'sla_config_no_id', string="Working Hour No")
    sla_config_time_na_ids = fields.One2many('sla_config_stages_na', 'sla_config_na_id', string="Working Hour N/A")

    @api.constrains('project_id')
    def validate_weekdays(self):
        template_rec = self.env['sla_config'].search([]) - self
        filtered_rec = template_rec.filtered(lambda x: x.project_id.id == self.project_id.id)
        if len(filtered_rec) > 0:
            raise ValidationError("The Project \"" + self.project_id.name + "\" already exists.")

    @api.constrains('sla_config_time_ids')
    def validation_defects(self):
        if len(self.sla_config_time_ids.ids) == 0:
            raise ValidationError('Warning! please add SLA Stage lines.')

    @api.model
    def default_get(self, fields_list):
        defaults = super(SLAConfig, self).default_get(fields_list)

        if 'sla_config_time_ids' in fields_list:
            defaults['sla_config_time_ids'] = [
                (0, 0, {'from_state': 'New', 'to_state': 'Acknowledged/Reject'}),
                (0, 0, {'from_state': 'Acknowledged', 'to_state': 'Progressive/Hold'}),
                (0, 0, {'from_state': 'Progressive', 'to_state': 'Fixed'}),
                (0, 0, {'from_state': 'Fixed', 'to_state': 'Closed/ReOpen'}),
                (0, 0, {'from_state': 'Reject', 'to_state': 'Closed/New'}),
                (0, 0, {'from_state': 'ReOpen', 'to_state': 'Acknowledged/Reject'}),
            ]

        if 'sla_config_time_no_ids' in fields_list:
            defaults['sla_config_time_no_ids'] = [
                (0, 0, {'from_state': 'New', 'to_state': 'Acknowledged/Reject'}),
                (0, 0, {'from_state': 'Acknowledged', 'to_state': 'Progressive/Hold'}),
                (0, 0, {'from_state': 'Progressive', 'to_state': 'Fixed'}),
                (0, 0, {'from_state': 'Fixed', 'to_state': 'Closed/ReOpen'}),
                (0, 0, {'from_state': 'Reject', 'to_state': 'Closed/New'}),
                (0, 0, {'from_state': 'ReOpen', 'to_state': 'Acknowledged/Reject'}),
            ]

        if 'sla_config_time_na_ids' in fields_list:
            defaults['sla_config_time_na_ids'] = [
                (0, 0, {'from_state': 'New', 'to_state': 'Acknowledged/Reject'}),
                (0, 0, {'from_state': 'Acknowledged', 'to_state': 'Progressive/Hold'}),
                (0, 0, {'from_state': 'Progressive', 'to_state': 'Fixed'}),
                (0, 0, {'from_state': 'Fixed', 'to_state': 'Closed/ReOpen'}),
                (0, 0, {'from_state': 'Reject', 'to_state': 'Closed/New'}),
                (0, 0, {'from_state': 'ReOpen', 'to_state': 'Acknowledged/Reject'}),
            ]

        return defaults


class SLAConfigStages(models.Model):
    _name = 'sla_config_stages'
    _description = 'sla_config_stages'

    from_state = fields.Selection(string="From Stage",
                                  selection=[('New', 'New'),
                                             ('Acknowledged', 'Acknowledged'),
                                             ('Progressive', 'Progressive'),
                                             ('Fixed', 'Fixed'),
                                             ('Reject', 'Reject'),
                                             ('ReOpen', 'ReOpen'),
                                             ])
    to_state = fields.Selection(string="To Stage",
                                selection=[('Acknowledged/Reject', 'Acknowledged/Reject'),
                                           ('Progressive/Hold', 'Progressive/Hold'),
                                           ('Fixed', 'Fixed'),
                                           ('Closed/ReOpen', 'Closed/ReOpen'),
                                           ('Closed/New', 'Closed/New'),
                                           ('Acknowledged/Reject', 'Acknowledged/Reject')
                                           ])
    time = fields.Float('Working Hour', required=True)
    sla_config_id = fields.Many2one('sla_config')


class SLAConfigStagesNo(models.Model):
    _name = 'sla_config_stages_no'
    _description = 'sla_config_stages_no'

    from_state = fields.Selection(string="From Stage",
                                  selection=[('New', 'New'),
                                             ('Acknowledged', 'Acknowledged'),
                                             ('Progressive', 'Progressive'),
                                             ('Fixed', 'Fixed'),
                                             ('Reject', 'Reject'),
                                             ('ReOpen', 'ReOpen'),
                                             ])
    to_state = fields.Selection(string="To Stage",
                                selection=[('Acknowledged/Reject', 'Acknowledged/Reject'),
                                           ('Progressive/Hold', 'Progressive/Hold'),
                                           ('Fixed', 'Fixed'),
                                           ('Closed/ReOpen', 'Closed/ReOpen'),
                                           ('Closed/New', 'Closed/New'),
                                           ('Acknowledged/Reject', 'Acknowledged/Reject')
                                           ])
    time = fields.Float('Working Hour', required=True)
    sla_config_no_id = fields.Many2one('sla_config')


class SLAConfigStagesNA(models.Model):
    _name = 'sla_config_stages_na'
    _description = 'sla_config_stages_na'

    from_state = fields.Selection(string="From Stage",
                                  selection=[('New', 'New'),
                                             ('Acknowledged', 'Acknowledged'),
                                             ('Progressive', 'Progressive'),
                                             ('Fixed', 'Fixed'),
                                             ('Reject', 'Reject'),
                                             ('ReOpen', 'ReOpen'),
                                             ])
    to_state = fields.Selection(string="To Stage",
                                selection=[('Acknowledged/Reject', 'Acknowledged/Reject'),
                                           ('Progressive/Hold', 'Progressive/Hold'),
                                           ('Fixed', 'Fixed'),
                                           ('Closed/ReOpen', 'Closed/ReOpen'),
                                           ('Closed/New', 'Closed/New'),
                                           ('Acknowledged/Reject', 'Acknowledged/Reject')
                                           ])
    time = fields.Float('Working Hour', required=True)
    sla_config_na_id = fields.Many2one('sla_config')
