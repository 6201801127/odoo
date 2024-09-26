# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo import tools, _
from odoo.exceptions import UserError


class kw_image_category(models.Model):
    _name = 'kw_image_category'
    _description = 'Categories of Gallery'
    _rec_name = 'name'

    category_id = fields.One2many('kw_image_albums', 'category_name', ondelete='strict')
    name = fields.Char(string="Category Name", required=True, size=100)
    description = fields.Text('Description')
    public = fields.Boolean('Is Public?',
                            help='This public means, the category only available to all the restricted publisher group.')
    no_of_albums = fields.Integer('Number of Albums', compute='count_albums')
    to_some_specific_group = fields.Many2many('res.groups')
    no_of_published_albums = fields.Integer('No of published albums', compute='count_publish_and_unpublish_albums',
                                            help='Count number of Published albums')
    no_of_unpublished_albums = fields.Integer('No of unpublished albums', compute='count_publish_and_unpublish_albums',
                                              help='Count number of Unpublished albums')

    @api.onchange('public')
    def remove_groups(self):
        for record in self:
            if record.public:
                record.to_some_specific_group = False

    def count_albums(self):
        for record in self:
            for data in record.category_id:
                for records in data.category_name:
                    record.no_of_albums += 1

    @api.multi
    def count_publish_and_unpublish_albums(self):
        for record in self:
            for datas in record.category_id:
                if datas.status == '3':
                    record.no_of_published_albums += 1
                else:
                    record.no_of_unpublished_albums += 1

    @api.model
    def create(self, vals):
        cat_record = super(kw_image_category, self).create(vals)
        if cat_record:
            self.env.user.notify_success(message='Image category created successfully')
        else:
            self.env.user.notify_danger(message='Image category creation failed')
        if cat_record.to_some_specific_group:
            # add the publisher group to the inherited group list
            cat_record.to_some_specific_group.write(
                {'implied_ids': [[4, self.env.ref('kw_gallery.group_kw_gallery_restricted_publisher').id, False]]})
        return cat_record

    @api.multi
    def write(self, vals):
        old_grp_recset = self.to_some_specific_group
        rec = super(kw_image_category, self).write(vals)
        # check groups those are deleted
        del_grp_recset = old_grp_recset - self.to_some_specific_group
        # get the id of publisher group
        publisher_grp_id = self.env.ref('kw_gallery.group_kw_gallery_restricted_publisher').id
        # add the publisher group to the inherited group list
        if self.to_some_specific_group:
            self.to_some_specific_group.write({'implied_ids': [[4, publisher_grp_id, False]]})
            # removes publisher group from the inherited group list
        if len(del_grp_recset) > 0:
            del_grp_recset.write({'implied_ids': [[3, publisher_grp_id, False]]})
        if rec:
            self.env.user.notify_success(message='Category updated successfully')
        else:
            self.env.user.notify_danger(message='Category updation failed')
        return rec

    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['kw_image_category'].search([('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError('Exists! Already a same category name exists in the gallery.')

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(kw_image_category, self).copy(default=default)

    def unlink(self):
        if any(data.no_of_albums > 0 for data in self):
            raise UserError(_('You can not delete the category, because it contains albums.'))
        else:
            self.env.user.notify_success(message='Category deleted successfully')
        return super(kw_image_category, self).unlink()
