# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests, json
from time import strftime, gmtime
import queue
from threading import Thread
from time import strftime, gmtime


# strftime("%S", gmtime())
class kw_synchronization(models.Model):
    _name = 'kw_synchronization'
    _rec_name = 'model_name'
    _description = 'Synchronization model for show the synchronize status.'

    model_name = fields.Char("Model name")
    new_data = fields.Char("New data")
    old_data = fields.Char("old data")
    operation = fields.Selection(string=u'Operation', selection=[('U', 'U'), ('I', 'I'), ('D', 'D')])
    sync_status = fields.Integer("Sync status", default=0)
    sync_message = fields.Text("Sync message", )
    sync_date = fields.Date(string=u'Sync date', default=fields.Date.context_today, )
    record_id = fields.Integer("Record ID", )

    def send_json_data(self, rec):

        # ### This part is according to the .net configuration , don't modify it. ###
        # url = 'http://172.27.37.145/prd.service.portalV6.csmpl.com/OdooSynSVC.svc/getMasterData'
        url = self.env['ir.config_parameter'].sudo().get_param('kwantify_json_data_url')
        header = str({'Model': rec.model_name, 'Operation': rec.operation, 'SyncBy': '45'})
        data = str(rec.new_data)
        json_data = {
            'Header': header,
            'Data': data,
        }

        header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        data = json.dumps(json_data)
        # ########################################################################################
        try:
            response_result = requests.post(url, data=data, headers=header, timeout=30)

            resp = json.loads(response_result.text)
            status = resp[0]['Status']
            sync_message = resp[0]['OutMessage']
            rec.write({
                'sync_status': int(status),
                'sync_message': sync_message,
            })

            model_record_id = self.env[rec.model_name].sudo().browse(rec.record_id)
            if len(model_record_id) > 0:
                model_record_id.write({"kw_id": resp[0]['KWId']})
        except:
            rec.write({
                'sync_status': 2,
                'sync_message': 'Request Timeout',
            })

    def _schedule_data(self):
        # que = queue.Queue()
        # threads_list = list()
        data = self.env['kw_synchronization'].sudo().search(['|', ('sync_status', '=', 0), ('sync_status', '=', 2)])
        # threads_list=[]
        for rec in data:
            self.send_json_data(rec)
            # t = Thread(target=lambda q, arg1: q.put(self.send_json_data(arg1)), args=(que,rec))
        #     t.start()
        #     threads_list.append(t)
        # for t in threads_list:
        #     t.join()
        # while not que.empty():
        #     result = que.get()
        #     print(result)
