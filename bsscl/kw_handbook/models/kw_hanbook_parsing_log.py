import base64
from odoo import models, fields, api, tools
from datetime import datetime,date
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO, StringIO
import re
from collections import defaultdict
# import pandas as pd
import PyPDF2
# from nltk.tokenize import word_tokenize, sent_tokenize




class Kw_Handbook_Parsing(models.Model):
    _name="handbook_parsing_log"
    _description = 'Documents log data'
    # _rec_name = 'title'



    name=fields.Char(string="Name")
    description=fields.Html(string="Description")
    job_role_id=fields.Many2one("hr.job.role",string="Job role")
    # designations=fields.Many2many(related="job_role_id.designations",string="Designations")
    
    
    
    
    def handbook_parsing_data(self):
        handbook_data = self.env['kw_onboarding_handbook'].sudo().search([])
        create_in_log=self.env['handbook_parsing_log']
        for rec in handbook_data:
            dms_data = self.env['kw_dms.file'].sudo().search([('id','=',rec.dms_file_id.id),('res_model','=','kw_onboarding_handbook'),('res_id','=',rec.id)], limit=1)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>dms_data>>>>>>>>>>>>>>>>>>>>>>>>>>>>", dms_data,type(dms_data.content))
            for dms in dms_data:
                dms_file = base64.b64decode(dms.content)
            # file_path = os.path.join(os.getcwd(), 'file.pdf')
            file_path = os.path.join('/home/localadmin/odoo12/kwantify-odoo', 'file.pdf')
            with open(file_path, 'wb') as f:
                f.write(dms_file)   

        pdf_text_pages = []

        with open(file_path, 'rb') as r:
            pages = [i for i in PDFPage.get_pages(r, caching=True, check_extractable=True)][7:38]
            for page in pages:
                resource_manager = PDFResourceManager()
                fake_file_handle = StringIO()
                converter = TextConverter(resource_manager, fake_file_handle, codec='utf-8', laparams=LAParams())
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()

                text = re.sub(r'\t+', ' ', text)

                pdf_text_pages.append('\n'.join(text.splitlines()[:-4]))
                converter.close()
                fake_file_handle.close()

            pdf_text_pages = [re.sub('\d{1,2}\)', '', i) for i in pdf_text_pages]

            pdf_text = '\n'.join(pdf_text_pages)

            topic_text = re.findall('\d\.\d{1,2}[\s\S]+?(?=\d\.\d{1,2})|\d\.\d{1,2}[\s\S]+$', pdf_text)

            total_data = defaultdict(list)

            for topic in topic_text:
                topic_data = [i.strip() for i in topic.split("\n\n") if not i.isspace()]

                total_data[topic_data[0]].extend(topic_data[1:])

          
            job_keys=total_data.keys()
            for title in job_keys:
                if title in total_data:
                    job_title = title.split(' ', 1)
                    job_title.pop(0) 
                    job_title_str = ' '.join(job_title) 
                    final_description = '<ol>'
                    for description in total_data[title]:
                        final_description += '<li>'+description+'</li>'
                    final_description += '</ol>'
                        
                    print("job_title_str >>>>>> ", type(job_title_str),type(create_in_log.name))
                    existing_record = self.env['handbook_parsing_log'].search([('name', '=', job_title_str),('description','=',final_description)])
                    if existing_record  : 
                        self.env.user.notify_success(message='Already updated successfully')
                        
                    else:
                        print("in else===================")
                        create_in_log.create({
                            'name': job_title_str,
                            'description': final_description,
                        })   
        