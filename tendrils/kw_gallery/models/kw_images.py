# -*- coding: utf-8 -*-

from distutils.command.upload import upload
from odoo import models, fields, api
from datetime import datetime


class kw_images(models.Model):
    _name = 'kw_images'
    _description = 'All images'

    image_id = fields.Many2one('kw_image_albums')
    title = fields.Char('Title')
    image = fields.Binary('Upload Image', attachment=True)
    video = fields.Char('Youtube Video URL')
    upload_status = fields.Selection(
        [('image', 'Image'), ('video', 'Video')], string="File Type", default="image")
    image_status = fields.Selection([('1', 'Published'), ('2', 'Unpublished')], default='2',
                                    track_visibility='onchange', string='Status')
    tag_employees = fields.Many2many('res.users')
    attachment_id = fields.Char(
        compute='_compute_attachment_id', string="Attachments")

    @api.multi
    def publish_image(self):
        for record in self:
            attachment = record.env['ir.attachment'].sudo().search(
                [('res_id', '=', record.id), ('res_model', '=', 'kw_images'), ('res_field', '=', 'image')])
            # print("attachment successfully=========",attachment)
            if attachment:
                attachment.public = True
                # print("updated successfully=========")

            record.image_status = '1'

    @api.multi
    def unpublish_image(self):
        for record in self:
            record.image_status = '2'

    def _compute_attachment_id(self):
        for image in self:
            attachment_id = self.env['ir.attachment'].search(
                [('res_id', '=', image.id), ('res_model', '=', 'kw_images'), ('res_field', '=', 'image')]).id
            image.attachment_id = attachment_id

    @api.onchange('upload_status')
    def onchange_upload_status(self):
        for record in self:
            record.image = False
            if record.upload_status == 'image':
                record.video = False

    # @api.onchange('upload_status')
    # def onchange_upload_status(self):
    #     if self.upload_status:
    #         if self.upload_status.image:
    #             self.image = self.upload_status.image
    #         elif self.upload_status.video:
    #             self.video=self.upload_status.video
    #     else:
    #         pass
