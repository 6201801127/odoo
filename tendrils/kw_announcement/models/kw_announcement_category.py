# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_announcement_category(models.Model):
    _name = 'kw_announcement_category'
    _description = "Announcement Category"

    name = fields.Char(string='Name', required=True, size=100)
    alias = fields.Char(string='Alias', required=True, size=100)
    enable_comment = fields.Boolean(string=u'Enable Comment', default=False)
    is_location_specific = fields.Boolean(string=u'Is Location Specific ?', default=False)
    assigned_groups = fields.Many2many('res.groups', string='Assigned Groups')

    @api.constrains('name', 'alias')
    def _validate_name(self):
        record = self.env['kw_announcement_category'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The name " + self.name + " already exists.")
            if info.alias.lower() == self.alias.lower():
                raise ValidationError("The alias " + self.alias + " already exists.")

    @api.onchange("name", )
    def _set_alias(self):
        for record in self:
            if record.name:
                record.alias = " ".join(record.name.split()).replace(' ', '_').lower()

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'The name already exists.. !'),
        ('alias_unique', 'unique (alias)', 'The alias already exists.. !')
    ]

    # method to override the create method
    @api.model
    def create(self, vals):

        cat_record = super(kw_announcement_category, self).create(vals)
        if cat_record.assigned_groups:
            # add the publisher group to the inherited group list
            cat_record.assigned_groups.write(
                {'implied_ids': [[4, self.env.ref('kw_announcement.group_kw_announcement_publisher').id, False]]})
        self.env.user.notify_success(message='Announcement category has created sucessfully')
        return cat_record

    @api.multi
    def write(self, vals):

        old_grp_recset = self.assigned_groups
        super(kw_announcement_category, self).write(vals)
        # check groups those are deleted
        del_grp_recset = old_grp_recset - self.assigned_groups
        # get the id of publisher group
        publisher_grp_id = self.env.ref('kw_announcement.group_kw_announcement_publisher').id
        # add the publisher group to the inherited group list
        if self.assigned_groups:
            self.assigned_groups.write({'implied_ids': [[4, publisher_grp_id, False]]})
            # removes publisher group from the inherited group list
        if len(del_grp_recset) > 0:
            del_grp_recset.write({'implied_ids': [[3, publisher_grp_id, False]]})
        return True
