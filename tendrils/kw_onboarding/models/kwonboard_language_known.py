# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class kwonboard_language_known(models.Model):
    _name = 'kwonboard_language_known'
    _description = "A  model to store different languages known by onboardings."

    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID", )
    language_id = fields.Many2one('kwemp_language_master', string="Language", required=True)
    reading_status = fields.Selection(string=u'Reading',
                                      selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight'), ],
                                      required=True)
    writing_status = fields.Selection(string=u'Writing',
                                      selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')],
                                      required=True)
    speaking_status = fields.Selection(string=u'Speaking',
                                       selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')],
                                       required=True)
    understanding_status = fields.Selection(string=u'Understanding',
                                            selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')],
                                            required=True)

    @api.constrains('reading_status', 'writing_status', 'speaking_status', 'understanding_status', 'language_id')
    def validate_language_status(self):
        for record in self:
            if not (record.reading_status):
                raise ValidationError("Please choose " + self.language_id.name + " language reading status.")
            elif not (record.writing_status):
                raise ValidationError("Please choose " + self.language_id.name + " language writing status.")
            elif not (record.speaking_status):
                raise ValidationError("Please choose " + self.language_id.name + " language speaking status.")
            elif not (record.understanding_status):
                raise ValidationError("Please choose " + self.language_id.name + " language understanding status.")

    _sql_constraints = [('language_uniq', 'unique (enrole_id,language_id)', 'Selected language already exists !')]
