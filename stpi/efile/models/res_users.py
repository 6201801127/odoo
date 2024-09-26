from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
import requests
import json
from odoo.exceptions import UserError

class ResUesrs(models.Model):
    _inherit= 'res.users'

    @api.model
    def create(self, vals):
        res = super(ResUesrs, self).create(vals)
        data = {
            'assign_name': res.folder_name,
            'assign_no': res.sequence,
            'assign_date': res.date,
            'assign_subject': (res.subject.subject),
            'remarks': res.description,
            'created_by': res.current_owner_id.id,
            'doc_flow_id': 0,
            'wing_id': res.department_id.id,
            'section_id': 0,
            'designation_id': res.job_id.id,
            'document_ids': res.document_ids,
        }
        req = requests.post('http://206.189.129.190/STPI/www/web-service/add-assignment/', data=data,
                            json=None)
        try:
            pastebin_url = req.text
            print('============Patebin url=================', pastebin_url)
            dictionary = json.loads(pastebin_url)
            print('=================str(res.current_owner_id.id)===========================',
                  str(res.current_owner_id.id))
            res.notesheet_url = str(dictionary["response"][0]['notesheet'])
            s = str(dictionary["response"][0]['notesheet'])
            print('=====================notesheet url==========================', s)
            print(s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
            d = (s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
            res.assignment_id = (d.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
            print('===============================res.assignment_id-----------', res.assignment_id)
            req.raise_for_status()
            status = req.status_code
            if int(status) in (204, 404):
                response = False
            else:
                response = req.json()
        return res


    @api.multi
    def create_file(self):
        for res in self:
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            print('====================CUrrent Employee====================', current_employee)
            seq = self.env['ir.sequence'].next_by_code('folder.master')
            res.sequence = int(seq)
            print('=======================assign_name========================', res.folder_name)
            print('=======================assign_no========================', res.sequence)
            print('=======================assign_date========================', res.date)
            print('=======================assign_subject========================', res.subject.subject)
            print('=======================rremarks========================', res.description)
            print('=======================created_by========================', res.current_owner_id)
            print('=======================wing_id========================', res.department_id.id)
            print('=======================designation_id========================', res.job_id.id)
            print('=======================document_ids========================', res.document_ids)
            data = {
                'assign_name': res.folder_name,
                'assign_no': res.sequence,
                'assign_date': res.date,
                'assign_subject': (res.subject.subject),
                'remarks': res.description,
                'created_by': res.current_owner_id.id,
                'doc_flow_id': 0,
                'wing_id': res.department_id.id,
                'section_id': 0,
                'designation_id': res.job_id.id,
                'document_ids': res.document_ids,
            }
            req = requests.post('http://206.189.129.190/STPI/www/web-service/add-assignment/', data=data,
                                json=None)
            try:
                pastebin_url = req.text
                print('============Patebin url=================', pastebin_url)
                dictionary = json.loads(pastebin_url)
                print('=================str(res.current_owner_id.id)===========================',
                      str(res.current_owner_id.id))
                res.notesheet_url = str(dictionary["response"][0]['notesheet'])
                s = str(dictionary["response"][0]['notesheet'])
                print('=====================notesheet url==========================', s)
                print(s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                d = (s.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                res.assignment_id = (d.replace('http://206.189.129.190/STPI/www/assignment/note-sheet/', ''))
                print('===============================res.assignment_id-----------', res.assignment_id)
                req.raise_for_status()
                status = req.status_code
                if int(status) in (204, 404):
                    response = False
                else:
                    response = req.json()
                current_employee = self.env['hr.employee'].search([('user_id', '=', res.current_owner_id.id)], limit=1)
                print('==================================current employee==========================',
                      current_employee.name)
                print('==================================current employee id==========================',
                      current_employee.id)
                print('==================================current employee job id==========================',
                      current_employee.job_id.name)
                print('==================================current employee department_id id==========================',
                      current_employee.department_id.name)
                print('==================================current employee branch id==========================',
                      current_employee.branch_id.name)
                print('==================================current employee user id==========================',
                      current_employee.user_id.name)
                return (status, response)
            except Exception as e:
                print('=============Error==========', e)