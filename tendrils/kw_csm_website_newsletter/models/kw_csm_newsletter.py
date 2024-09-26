# -*- coding: utf-8 -*-
from odoo import models, fields, api
import html


class kw_csm_newsletter(models.Model):
    _name = "kw_csm_newsletter"
    _description = "csm website newsletter"
    _rec_name = 'subject'

    subject = fields.Char("Subject")
    body = fields.Html("Body")
    mode = fields.Char("Mode")
    type = fields.Char("Type")
    url = fields.Char("URL")

    # page_ids = fields.One2many('kw_csm_page_history','news_letter_id',string='Page Ids')
    page_id = fields.Many2one('kw_csm_page_history', 'New Letter ID')

    # #overwrite the create method
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
            @return: returns a id of new record
        """

        values['body'] = html.unescape(values['body'])

        page_model = self.env['kw_csm_page_history']
        if 'page_id' not in values:
            page_record = False

            if values['mode'] == 'weekly':
                page_record = page_model.search([('is_sent', '=', False), ('mode', '=', values['mode']), ('type', '=', values['type'])], limit=1)

            if not page_record or values['mode'] == 'immediate':
                page_record = page_model.create({'mode': values['mode'], 'type': values['type']})

            values['page_id'] = page_record.id
        result = super(kw_csm_newsletter, self).create(values)

        if values['mode'] == 'immediate':
            page_model.send_newsletter_mail('immediate')

        return result


class kw_csm_page_history(models.Model):
    _name = "kw_csm_page_history"
    _description = "csm page history"
    # _rec_name = 'mode'
    _order = "create_date desc"

    mode = fields.Char("Mode")
    is_sent = fields.Boolean("Is Sent?", default=False)
    news_letter_ids = fields.One2many('kw_csm_newsletter', 'page_id', string='Subjects')
    type = fields.Char("Type")
    
    @api.model
    def send_newsletter_mail(self, *args):
        # update type for existing records if null
        self.update_newsletter_type()

        mode = args[0] if len(args) > 0 else ''
        # print('mode : ', mode)
        if mode == 'immediate':
            news_letter_records = self.env['kw_csm_page_history'].search([('is_sent', '=', False), ('mode', '=', 'immediate'), ])
        else:
            news_letter_records = self.env['kw_csm_page_history'].search([('is_sent', '=', False), ('mode', '=', 'weekly'), ])

        # for record in news_letter_records:
        #     template = self.env.ref('kw_csm_website_newsletter.kw_news_letter_email_template')
        #     template_data = self.env['mail.template'].browse(template.id)
        #     template_data.send_mail(record.id)
        #     record.write({'is_sent': True})

        template = self.env.ref('kw_csm_website_newsletter.kw_news_letter_email_template_new')
        template_data = self.env['mail.template'].browse(template.id)
        if news_letter_records:
            template_data.with_context(record=news_letter_records).send_mail(news_letter_records[0].id)

            for record in news_letter_records:
                record.write({'is_sent': True})
        return True

    @api.multi
    def get_groups_users_email(self):
        group = self.env.ref('kw_csm_website_newsletter.group_news_letter_manager')

        if group.users:
            manager_emp = self.env['hr.employee'].sudo().search([('user_id', 'in', group.users.ids)])
            # print("Manager emp mail=====",manager_emp)
            if manager_emp:
                emails = manager_emp.mapped('work_email')
                return ','.join(emails)

    @api.model
    def update_newsletter_type(self):
        page_model = self.env['kw_csm_page_history']
        news_letter_records = page_model.search([('type', '=', None), ('is_sent', '=', False), ])
        for record in news_letter_records:
            temp_dict = {}
            for child in record.news_letter_ids:
                if child.type in temp_dict:
                    child.page_id = temp_dict[child.type]
                else:
                    result = page_model.create({'mode': record['mode'], 'type': child['type']})
                    temp_dict.update({child.type: result.id})
                    child.page_id = result.id
            record.is_sent = True
        return True
