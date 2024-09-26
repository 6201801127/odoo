# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GreetingsResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    greetings_birthday_category = fields.Many2one('kw_greetings_category', string=u'Default Birthday Category',
                                                  ondelete='set null', )
    greetings_year_of_service_category = fields.Many2one('kw_greetings_category',
                                                         string=u'Default Year of Service Category',
                                                         ondelete='set null', )
    greetings_anniversary_category = fields.Many2one('kw_greetings_category', string=u'Default Anniversary Category',
                                                     ondelete='set null', )
    greetings_well_wish_category = fields.Many2one('kw_greetings_category', string=u'Default Well Wish Category',
                                                   ondelete='set null', )

    @api.model
    def get_values(self):
        res = super(GreetingsResConfigSettings, self).get_values()

        res.update(
            greetings_birthday_category=int(
                self.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_birthday_category')),
            greetings_year_of_service_category=int(
                self.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_year_of_service_category')),
            greetings_anniversary_category=int(
                self.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_anniversary_category')),
            greetings_well_wish_category=int(
                self.env['ir.config_parameter'].sudo().get_param('kw_greetings.greetings_well_wish_category')),
        )
        return res

    @api.multi
    def set_values(self):
        super(GreetingsResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.greetings_birthday_category.id or False
        field2 = self.greetings_year_of_service_category.id or False
        field3 = self.greetings_anniversary_category.id or False
        field4 = self.greetings_well_wish_category.id or False

        param.set_param('kw_greetings.greetings_birthday_category', field1)
        param.set_param('kw_greetings.greetings_year_of_service_category', field2)
        param.set_param('kw_greetings.greetings_anniversary_category', field3)
        param.set_param('kw_greetings.greetings_well_wish_category', field4)
