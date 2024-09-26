from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import requests
import json

class FileWizard(models.Model):
    _name = 'file.wizard'
    _description = 'Wizard of File Wizard'
    _rec_name = 'user'



    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')

    remarks = fields.Text('Remarks')

    defid = fields.Many2one('muk_dms.file', invisible=1)
    sec_own_ids = fields.One2many('secondary.file.owner', 'sec_own_id')



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
        for res in self:
            if res.user.id == False:
                raise UserError(_("%s is not configured to owned this file") % res.employee.name)
            else:
                print('================defid========================',res.defid.name)
                print('================defid.current_owner_id========================',res.defid.current_owner_id)
                print('================res.env.user.id========================',res.env.user.id)

                if res.defid.current_owner_id.id == res.env.user.id:
                    print('================True========================')
                    current_employee  = res.env['hr.employee'].search([('user_id', '=', res.defid.current_owner_id.id)], limit=1)
                    print('================current_employee========================', current_employee)
                    # sec_own = []
                    # previous_owner = []
                    #
                    # previous_owner.append(res.defid.current_owner_id.id)
                    # Previous owner append
                    transfer_to_emp = res.env['hr.employee'].search([('user_id', '=', res.defid.current_owner_id.id)], limit=1)
                    res.defid.previous_owner_emp = [(4, transfer_to_emp.id)]
                    # Last owner id created
                    res.defid.last_owner_id = res.defid.current_owner_id.id
                    # Current Owner id created
                    res.defid.current_owner_id = res.user.id
                    res.defid.responsible_user_id = res.user.id
                    # Secondary Owner id created
                    for line in res.sec_own_ids:
                        res.defid.sec_owner = [(4, line.employee.user_id.id)]
                        # Extra line
                        res.defid.previous_owner = [(4, line.employee.user_id.id)]
                        # sec_own.append(line.employee.user_id.id)
                    # res.defid.sec_owner = [(6,0,sec_own)]
                    res.env['file.tracking.information'].create({
                        'create_let_id': res.defid.id,
                        'forwarded_date': datetime.now().date(),
                        'forwarded_to_user': res.user.id,
                        'forwarded_to_dept': res.department.id,
                        'job_pos': res.jobposition.id,
                        'forwarded_by':res.env.uid,
                        'remarks':res.remarks
                    })
                    res.env['file.tracker.report'].create({
                        'name': str(res.defid.name),
                        'number': str(res.defid.letter_number),
                        'type': 'Correspondence',
                        'forwarded_by': str(current_employee.user_id.name),
                        'forwarded_by_dept': str(current_employee.department_id.name),
                        'forwarded_by_jobpos': str(current_employee.job_id.name),
                        'forwarded_by_branch': str(current_employee.branch_id.name),
                        'forwarded_date': datetime.now().date(),
                        'forwarded_to_user': str(res.user.name),
                        'forwarded_to_dept': str(res.department.name),
                        'job_pos': str(res.jobposition.name),
                        'forwarded_to_branch': str(res.user.branch_id.name),
                        'action_taken': 'correspondence_forwarded',
                        'remarks': res.remarks,
                        'details': 'Correspondence Forwarded'
                    })
                else:
                    # pass
                    raise ValidationError("You are not able to forward this file, as you are not the Primary owner of this file")
            return {
                'name': 'Incoming correspondence',
                'view_type': 'form',
                'view_mode': 'kanban,tree,graph,pivot,form',
                'res_model': 'muk_dms.file',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }



class SecondaryOwners(models.Model):
    _name = 'secondary.file.owner'
    _description = 'Secondary Owners'

    sec_own_id = fields.Many2one('file.wizard')
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

