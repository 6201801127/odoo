from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class FileWizard(models.Model):
    _name = 'folder.wizard'
    _description = 'Wizard of File Wizard'
    _rec_name = 'user'

    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')
    remarks = fields.Text('Remarks')

    defid = fields.Many2one('folder.master', invisible=1)
    sec_own_ids = fields.One2many('secondary.folder.owner', 'sec_own_id')



    @api.onchange('department','jobposition')
    def _onchange_user(self):
        for rec in self:
            if rec.department.id and not rec.jobposition.id:
                return {'domain': {'employee': [('department_id', '=', rec.department.id)]}}
            elif rec.jobposition.id and not rec.department.id:
                return {'domain': {'employee': [('job_id', '=', rec.jobposition.id)]}}
            elif rec.jobposition.id and rec.department.id:
                return {'domain': {'employee': [('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}
            else:
                return {'domain': {'employee': ['|', ('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}


    def confirm_button(self):
        for rec in self:
            if rec.user.id == False:
                raise UserError(_("%s is not configured to owned this file") % rec.employee.name)
            else:
                if rec.defid.current_owner_id.id == rec.env.user.id:
                    file_count = 0
                    sec_own = []
                    previous_owner = []
                    previous_owner.append(rec.defid.current_owner_id.id)
                    rec.defid.previous_owner = [(4, rec.defid.current_owner_id.id)]
                    rec.defid.sec_owner = [(4, rec.defid.current_owner_id.id)]
                    print('========================================po=======================',rec.defid.current_owner_id.id)
                    print('========================================previous_owner=======================',previous_owner)
                    print('========================================rec.defid.previous_owner=======================',rec.defid.previous_owner)
                    rec.defid.last_owner_id = rec.env.user.id
                    rec.defid.current_owner_id = rec.user.id

                    current_employee  = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                    self.env['folder.tracking.information'].create({
                        'create_let_id': rec.defid.id,
                        'forwarded_date': datetime.now().date(),
                        'forwarded_to_user': rec.user.id,
                        'forwarded_to_dept': rec.department.id,
                        'job_pos': rec.jobposition.id,
                        'forwarded_by': rec.env.uid,
                        'remarks': rec.remarks
                    })

                    print('==============================to_designation_id=============================', rec.jobposition.id)
                    print('==============================to_user_id=============================', rec.user.id)
                    print('==============================remarks=============================', rec.remarks)
                    print('==============================to_designation_ids=============================', rec.jobposition.id)
                    print('==============================to_user_ids=============================', rec.user.id)
                    print('==============================user_id=============================', rec.env.user.id)
                    print('==============================assignment_id=============================', rec.defid.assignment_id)
                    data = {
                        'is_action_taken': 'F',
                        'assignment_flag': 1,
                        'to_designation_id': rec.jobposition.id,
                        'to_user_id': rec.user.id,
                        'remarks': rec.remarks,
                        'to_designation_ids': rec.jobposition.id,
                        'to_user_ids': rec.user.id,
                        'user_id': rec.env.user.id,
                        'assignment_id': rec.defid.assignment_id,
                    }

                    req = requests.post('http://206.189.129.190/STPI/www/web-service/forward-correspondence/', data=data,
                                        json=None)

                    try:
                        print('=====================================================', req)
                        pastebin_url = req.text
                        dictionary = json.loads(pastebin_url)
                        rec.defid.iframe_dashboard = str(dictionary["response"][0]['notesheet']) + str('?type=STPI&user_id=') + str(rec.user.id)
                        print('===========================url==========================', rec.defid.iframe_dashboard)
                        print('===========================pastebin_url==========================', pastebin_url)
                    except Exception as e:
                        print('=============Error==========', e)

                    f_details = ""
                    if file_count == 0:
                        f_details = "File forwarded with no correspondence"
                    elif file_count == 1:
                        f_details = "File forwarded with single correspondence"
                    elif file_count > 1:
                        f_details = "File forwarded with multiple Correspondence"
                    else:
                        f_details = ""
                    self.env['file.tracker.report'].create({
                        'name': str(rec.defid.folder_name),
                        'number': str(rec.defid.number),
                        'type': 'File',
                        'forwarded_by': str(current_employee.user_id.name),
                        'forwarded_by_dept': str(current_employee.department_id.name),
                        'forwarded_by_jobpos': str(current_employee.job_id.name),
                        'forwarded_by_branch': str(current_employee.branch_id.name),
                        'forwarded_date': datetime.now().date(),
                        'forwarded_to_user': str(rec.user.name),
                        'forwarded_to_dept': str(rec.department.name),
                        'forwarded_to_branch': str(rec.user.branch_id.name),
                        'job_pos': str(rec.jobposition.name),
                        'action_taken': 'file_forwarded',
                        'remarks': rec.remarks,
                        'details': f_details
                    })
                    sec_own = []
                    previous_owner = []
                    for file in rec.defid.file_ids:
                        file_count+=1
                        file.last_owner_id = rec.env.user.id
                        file.responsible_user_id = rec.env.user.id
                        file.current_owner_id = rec.user.id
                        for line in rec.sec_own_ids:
                            sec_own.append(line.employee.user_id.id)
                        file.sec_owner = [(6, 0, sec_own)]

                        previous_owner.append(rec.env.user.id)

                        file.previous_owner = [(6, 0, previous_owner)]

                        self.env['file.tracking.information'].create({
                            'create_let_id': file.id,
                            'forwarded_date': datetime.now().date(),
                            'forwarded_to_user': rec.user.id,
                            'forwarded_to_dept': rec.department.id,
                            'job_pos': rec.jobposition.id,
                            'forwarded_by':rec.env.uid,
                            'remarks': rec.remarks
                        })
                        self.env['file.tracker.report'].create({
                            'name': str(file.name),
                            'number': str(file.letter_number),
                            'type': 'Correspondence',
                            'forwarded_by': str(current_employee.user_id.name),
                            'forwarded_by_dept': str(current_employee.department_id.name),
                            'forwarded_by_jobpos': str(current_employee.job_id.name),
                            'forwarded_by_branch': str(current_employee.branch_id.name),
                            'forwarded_date': datetime.now().date(),
                            'forwarded_to_user': str(rec.user.name),
                            'forwarded_to_dept': str(rec.department.name),
                            'job_pos': str(rec.jobposition.name),
                            'forwarded_to_branch': str(rec.user.branch_id.name),
                            'action_taken': 'correspondence_forwarded',
                            'remarks': rec.remarks,
                            'details': "Correspondence Forwarded through File {}".format(rec.defid.number)
                        })
                    rec.defid.write({'state': 'in_progress'})
                    print('========================================rec.defid.previous_owner=======================',rec.defid.previous_owner.ids)
                else:
                    raise ValidationError("You are not able to forward this file, as you are not the Primary owner of this file")

            return {
                'name': 'Incoming Files',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'folder.master',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }


class SecondaryOwners(models.Model):
    _name = 'secondary.folder.owner'
    _description = 'Secondary Owners'

    sec_own_id = fields.Many2one('folder.wizard')
    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')


    @api.onchange('department','jobposition')
    def _onchange_user(self):
        for rec in self:
            if rec.department.id and not rec.jobposition.id:
                return {'domain': {'employee': [('department_id', '=', rec.department.id)]}}
            elif rec.jobposition.id and not rec.department.id:
                return {'domain': {'employee': [('job_id', '=', rec.jobposition.id)]}}
            elif rec.jobposition.id and rec.department.id:
                return {'domain': {'employee': [('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}
            else:
                return {'domain': {'employee': ['|', ('job_id', '=', rec.jobposition.id),('department_id', '=', rec.department.id)]}}

