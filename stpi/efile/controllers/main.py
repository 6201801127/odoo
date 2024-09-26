from odoo import http
from odoo.http import request


class PartnerProvider(http.HttpRequest):
   @http.route(['/files/list'], type='json', auth='public', methods=['POST'])
   def send_users(self, **kwargs):
       if len(kwargs) == 0:
           cr = self.env.cr
           query = """
           SELECT * FROM folder_master
           """
           cr.execute(query)
           files = cr.dictfetchall()
           return {
               'files': files,
           }
       elif len(kwargs) == 1:
           cr = self.env.cr
           query = """
                       SELECT * FROM folder_master WHERE id = %s
                       """ %kwargs['id'] # Assuming that the data from the client contains the id of the partner
           cr.execute(query)
           file = cr.dictfetchall()
           return {
               'files': file,
           }