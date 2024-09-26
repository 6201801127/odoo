# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import tools, _
from odoo.exceptions import UserError
from odoo import http


class kw_image_albums(models.Model):
    _name = 'kw_image_albums'
    _description = 'Kwantify Image Albums'
    _rec_name = 'name'

    category_name = fields.Many2one('kw_image_category', ondelete='restrict')
    gallery_id = fields.One2many('kw_images', 'image_id')
    # , domain=[('image_status', '=', 1)]

    name = fields.Char(string="Album Name", size=100)
    description = fields.Text('Description')
    no_of_pictures = fields.Integer('Number of Pictures', compute='count_photos', store=True)
    status = fields.Selection([('1', 'Draft'), ('2', 'Post'), ('3', 'Published')], required=True, default='1',
                              track_visibility='onchange')
    count_unpublished_images = fields.Integer('No of unpublished images', compute='count_publish_images')
    published_pictures = fields.Integer('Number of published pictures', compute='count_publish_images')
    color = fields.Integer("Color Index", compute="change_color")

    @api.multi
    def post_album(self):
        for record in self.gallery_id:
            if record.image_status == '2':
                record.image_status = '1'
        self.status = '2'

    @api.multi
    def keep_in_draft_album(self):
        self.status = '1'

    @api.depends('status')
    def change_color(self):
        for record in self:
            color = 0
            if record.status == '1':
                color = 9
            elif record.status == '2':
                color = 4
            elif record.status == '3':
                color = 10
            record.color = color
    
    @api.constrains('name')
    def _check_name(self):
        record = self.env['kw_image_albums'].sudo().search([]) - self
        for data in record:
            if self.category_name == data.category_name and self.name.lower() == data.name.lower():
                raise ValidationError("The album {} is already exists , try a different one.".format(data.name))

    # @api.constrains('gallery_id')
    # def _check_gallery_title(self):
    #     image_names = []
    #     for each_record in self.gallery_id:
    #         for image in each_record:
    #             if image.title.lower() not in image_names:
    #                 image_names.append(image.title.lower())
    #             else:
    #                 raise ValidationError("The title {} is duplicate.".format(image.title))
    #     record = self.env['kw_image_albums'].sudo().search(
    #         ['&', ('category_name', '=', self.category_name.id), ('name', '=', self.name)]) - self
    #     if len(record):
    #         for each_record in record.gallery_id:
    #             for image in each_record:
    #                 if image.title.lower() in image_names:
    #                     raise ValidationError("The title {} is already exists".format(image.title))

    @api.model
    def create(self, vals):
        new_records = super(kw_image_albums, self).create(vals)
        if new_records:
            self.env.user.notify_success(message='Album created successfully')
        else:
            self.env.user.notify_danger(message='Album creation failed')
        # if new_records.no_of_pictures == 0:
        #     raise ValidationError('Please upload an image.')
        # else:
        return new_records

    @api.multi
    def write(self, vals):
        res = super(kw_image_albums, self).write(vals)
        if res:
            self.env.user.notify_success(message='Album updated successfully')
        else:
            self.env.user.notify_danger(message='Album updation failed')
        if self.no_of_pictures == 0:
            raise ValidationError('Album can not be created without images.')
        else:
            return res

    @api.multi
    def publish_album(self):
        for record in self.gallery_id:
            # print(record.image_status)
            if record.image_status == '2':
                record.image_status = '1'
        self.status = '3'
        # self.env.user.notify_success(
        #     message=self.name + ' <i class="fa fa-folder"></i>' + '<br> album has published by ' + '<br>' + str(
        #         self.env.user.name_get()[0][1]) + '. <i class="fa fa-user"></i>')

        # channel = self.env['mail.channel'].sudo().search([('name', '=', 'general')])
        # notification = (
        #                    '<div><a href="" class="o_redirect" data-oe-id="%s">%s <i class="fa fa-folder"></i></a></div> <img src="kw_gallery/static/description/icon.png" height="50px" width="50px"/>') % (
        #                self.id, self.name)
        # channel.message_post(
        #     body='<b>' + notification + '</b>' + ' <br>album has been published in the Image gallery ' + '<br>Created by : <b class="text-success"> ' + str(
        #         self.env['res.users'].sudo().search(
        #             [('id', '=', self.create_uid.id)]).name) + ' ' + '<i class="fa fa-user"></i> </b>',
        #     subtype='mail.mt_comment')
        for record in self.gallery_id:
            if record.tag_employees:
                for user in record.tag_employees:
                    ch_obj = self.env['mail.channel']
                    if user.id:
                        channel1 = user.name + ', ' + self.env.user.name
                        channel2 = self.env.user.name + ', ' + user.name
                        channel = ch_obj.sudo().search(
                            ["|", ('name', 'ilike', str(channel1)), ('name', 'ilike', str(channel2))])
                        # print(" Channel is ", channel.name)
                        if not channel:
                            channel_id = ch_obj.channel_get([user.partner_id.id])
                            channel = ch_obj.browse([channel_id['id']])
                        channel.message_post(body=str(self.create_uid.name) + ' , tagged you in an image .',
                                             message_type='comment', subtype='mail.mt_comment',
                                             author_id=self.env.user.partner_id.id,
                                             notif_layout='mail.mail_notification_light')

    @api.depends('gallery_id')
    def count_photos(self):
        for record in self:
            for data in record.gallery_id:
                for images in data.image_id:
                    record.no_of_pictures += 1

    @api.multi
    def count_publish_images(self):
        for record in self:
            for data in record.gallery_id:
                if data.image_status == '1':
                    record.published_pictures += 1
                if data.image_status == '2':
                    record.count_unpublished_images += 1

    @api.multi
    def reject_album(self):
        self.status = '2'
        # self.env.user.notify_success(message='<b>"'+ self.name +'"</b> album rejected by ' + str(self.env.user.name_get()[0][1]))
    @api.multi
    def get_all_images(self):
        # kanban_view_id = self.env.ref("kw_gallery.gallery_detail_template").id
        image_list = [record.id for record in self.gallery_id if record.image_status == "1"]
        if len(image_list) > 0:
            return {
                'name': self.name,
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url':'/gallery-details-%s' % (self.id)
            }
        else:
            self.env.user.notify_info(
                message='<h4>There is no picture in this album. <i class="fa fa-frown-o"></i> </h4>')
        
        # return {
        #     'type':'ir.actions.client',
        #     'name':self.name,
        #     'tag':'kw_gallery_image.imageviewer',
        # }

    # @api.multi
    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     self.ensure_one()
    #     default = dict(default or {})
    #     print(default)
    #     if 'name' not in default:
    #         default['name'] = _("%s (copy)") % (self.name)
    #     return super(kw_image_albums, self).copy(default=default)

    def unlink(self):
        if any(data.status in '3' and not self.env.user.has_group('kw_gallery.group_kw_gallery_publisher') for data in
               self):
            raise UserError(_('You can not delete the published albums.'))
        return super(kw_image_albums, self).unlink()


    def btn_demo(self):
        for record in self:
            record_lst = record.gallery_id.ids
            record_set = self.env['kw_images'].sudo().search([('id','in',record_lst)])
            record_set.publish_image()


    def unpublish_image(self):
        for record in self:
            record_lst = record.gallery_id.ids
            record_set = self.env['kw_images'].sudo().search([('id','in',record_lst)])
            record_set.unpublish_image()

    def get_upload_images(self):
        for rec in self:
            view_id = self.env.ref('kw_gallery.kw_upload_many_images_form').id
            return {
                'name': 'Upload Images',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_upload_images_wizard',
                'target': 'new',
                'context':{
                'default_gallery_id': rec.id
            }
            }


class UploadImages(models.TransientModel):
    _name = 'kw_upload_images_wizard'
    _description = 'Upload Many Images At a Time'

    image_ids = fields.Many2many('ir.attachment', string='Images', required=True)
    gallery_id = fields.Many2one('kw_image_albums')
    title = fields.Char('Title')

    @api.constrains('image_ids')
    def _check_image_size(self):
        for image in self.image_ids:
            if image.file_size > 2 * 1024 * 1024:
                raise ValidationError("Image '{}' exceeds the maximum allowed size of 2 MB.".format(image.name))

    def upload_image(self):
        for rec in self.image_ids:
            # print(rec)
            if self.gallery_id:
                self.gallery_id.gallery_id.create({
                    'image_id': self.gallery_id.id,
                    'upload_status':'image',
                    'image':rec.datas,
                    'title':self.title
                })



    
        
        


