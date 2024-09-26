import base64
from odoo import models, fields, api, tools
from datetime import datetime, date
import os, io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO, StringIO
import re
from collections import defaultdict
import PyPDF2
from PyPDF2 import PdfFileReader
# import pandas as pd
import PyPDF2

from odoo.exceptions import ValidationError


# from nltk.tokenize import word_tokenize, sent_tokenize


class Kw_Handbook_Parsing(models.Model):
    _name = "handbook_parsing_log"
    _description = 'Documents log data'
    _order = 'name asc'

    doc_name = fields.Char(string="Doc Name")
    name = fields.Char(string="Name", required=True)
    description = fields.Html(string="Description")
    job_role_id = fields.Many2one("hr.job.role", string="Job Role")

    @api.depends('job_role_id')
    def _get_mapped_jobs(self):
        for rec in self:
            rec.designations = ', '.join(rec.job_role_id.sudo().designations.mapped('name')) if rec.job_role_id.sudo().designations else 'NA'
    designations = fields.Char(compute="_get_mapped_jobs", string="Designations")

    def action_sync_jd(self):
        for rec in self:
            if rec.job_role_id:
                rec.job_role_id.description = rec.description
            else:
                jd_rec = self.env['hr.job.role'].sudo().search([('name', '=', rec.name)])
                if not jd_rec.exists():
                    new_jd_rec = self.env['hr.job.role'].sudo().create({'name': rec.name, 'description': rec.description})
                    rec.job_role_id = new_jd_rec.id
                else:
                    rec.job_role_id = jd_rec.id
                    raise ValidationError('Exists ! Already a record exists in this name')

    @api.multi
    def handbook_parsing_data(self):
        handbook_data = self.env['kw_onboarding_handbook'].sudo().search([('handbook_type_id.code', '=', 'DEP')])
        create_in_log = self.env['handbook_parsing_log']
        # print("handbook_data >>>> ", handbook_data)
        # return
        for rec in handbook_data:
            dms_data = self.env['kw_dms.file'].sudo().search(
                [('id', '=', rec.dms_file_id.id), ('res_model', '=', 'kw_onboarding_handbook'),
                 ('res_id', '=', rec.id)], limit=1)
            # dms_data.content,
            # for dms in dms_data:
            #     dms_file = base64.b64decode(dms.content)
            # # file_path = os.path.join(os.getcwd(), 'file.pdf')
            # file_path = os.path.join('/tmp/', 'file.pdf')
            # with open(file_path, 'wb') as f:
            #     f.write(dms_file)
            # return
            pdf_text_pages = []
            content_file = dms_data.content_file
            # print(" >>>>>>>>>> ", type(content_file), type(dms_data.content_file))
            # content_file = base64.b64decode(base64.b64encode(dms_data.content_file))
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>dms_data>>>>>>>>>>>>>>>>>>>>>>>>>>>>", content_file)
            # string_out = io.BytesIO(content_file)
            # string_out = io.BytesIO()
            # string_out.write(dms_data.content)
            # content_file = string_out.getvalue()
            # print(" >>>>>>>>>> ", type(content_file))
            # return
            with io.BytesIO(content_file) as file:
                reader = PdfFileReader(file, strict=False)
                num_pages = len(reader.pages)
                # print(num_pages)
                start = rec.starting_page_num
                end = rec.ending_page_num
                pages = [i for i in PDFPage.get_pages(file, caching=True, check_extractable=True)][start:end]  # [6:39]
                # print(pages)
                for page in pages:
                    resource_manager = PDFResourceManager()
                    fake_file_handle = StringIO()
                    #  codec='utf-8',
                    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
                    page_interpreter = PDFPageInterpreter(resource_manager, converter)
                    page_interpreter.process_page(page)
                    text = fake_file_handle.getvalue()

                    text = re.sub(r'\t+', ' ', text)

                    pdf_text_pages.append('\n'.join(text.splitlines()[:-4]))
                    converter.close()
                    fake_file_handle.close()

                pdf_text_pages = [re.sub('\d{1,2}\)', '', i) for i in pdf_text_pages]
                # print("pdf_text_pages  ================= ", pdf_text_pages)
                pdf_text = '\n'.join(pdf_text_pages)
                # print("pdf_text ===================== ", pdf_text)
                topic_text = re.findall(r'(\d{1,2}\.\d{1,2}[\s\S]+?(?=\d{1,2}\.\d{1,2})|\d{1,2}\.\d{1,2}[\s\S]+)$', pdf_text)
                # print("topic_text >>>>>>>>>>>>> ", topic_text)
                total_data = defaultdict(list)

                for topic in topic_text:
                    topic_data = [i.strip() for i in topic.split("\n\n") if not i.isspace()]
                    # print("topic_data >>>> ", topic_data)
                    total_data[topic_data[0]].extend(topic_data[0:])

                job_keys = total_data.keys()

                # print("total_data >>> ", total_data)
                # print(" >> job_keys >>>>>>>>>>> ", job_keys)
                for title in job_keys:
                    if title in total_data:
                        job_title = title.split(' ', 1)
                        job_title.pop(0)
                        job_title_str = ' '.join(job_title)

                        final_description = '<ol>'
                        # print("total_data[title] >>>>>>>>>>>>>>>>>>>> ", total_data[title])
                        for description in total_data[title][1:]:
                            # print(" >>>>> >>>>>>>>>>>>>>>>>>>>> ", description)
                            if description.strip() != '':
                                final_description += '<li>' + description.strip() + '</li>'
                        final_description += '</ol>'

                        # print("job_title_str >>>>>> ", type(job_title_str), type(create_in_log.name))
                        existing_record = self.env['handbook_parsing_log'].search([('name', '=', job_title_str)])
                        if existing_record:
                            existing_record.write({
                                'doc_name': rec.title
                            })
                            # existing_record.write({
                            #     'name': job_title_str,
                            #     'description': final_description,
                            # })
                            # self.env.user.notify_success(message='Already updated successfully')
                            # print("Already updated successfully  >>>>>>>>>>>>>>>> ")
                        else:
                            # print("in else  ===================")
                            create_in_log.create({
                                'name': job_title_str,
                                'description': final_description,
                                'doc_name': rec.title
                            })
