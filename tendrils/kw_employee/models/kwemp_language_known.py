# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError


# from odoo import tools, _
# import re
# from lxml import etree
# from datetime import date, datetime
# from dateutil import relativedelta


##for language known details
class kwemp_language_known(models.Model):
    _name = 'kwemp_language_known'
    _description = "Employees languages known"
    _rec_name = "language_id"

    kw_id = fields.Integer(string='Tendrils ID')
    emp_id = fields.Many2one('hr.employee', ondelete='cascade', string="Employee ID", )
    # onboard_id = fields.Many2one('kwonboard_all',ondelete='cascade', string="Onboard ID")
    language_id = fields.Many2one('kwemp_language_master', string="Language", required=True)

    reading_status = fields.Selection(
        string=u'Reading',
        selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight'), ], required=True
    )
    writing_status = fields.Selection(
        string=u'Writing',
        selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')], required=True
    )
    speaking_status = fields.Selection(
        string=u'Speaking',
        selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')], required=True
    )
    understanding_status = fields.Selection(
        string=u'Understanding',
        selection=[('good', 'Good'), ('fair', 'Fair'), ('slight', 'Slight')], required=True
    )

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

    _sql_constraints = [('language_uniq', 'unique (emp_id,language_id)',
                         'The language  is exists.. !')]
