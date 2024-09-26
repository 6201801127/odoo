from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class GroupMaster(models.Model):
    _name = 'stpi.group.master'
    _description = 'Group Master'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True)
    description = fields.Text('Description')

class HrPaySlip(models.Model):
    _name='hr.payslip.paylevel'
    _description ='HR Payroll'

    name = fields.Char(string='Name')
    pay_band_from = fields.Integer(string='Pay Cell: From')
    pay_band_to = fields.Integer(string='Pay Cell: To')
    grade_pay= fields.Integer(string='Grade Pay')
    entry_pay_ids = fields.One2many('payslip.pay.level', 'entry_pay_id', string='Entry Pay Ids')
    #start: added by gouranga (2 july 2021)
    group_id = fields.Many2one("stpi.group.master","Group")
    #end: added by gouranga (2 july 2021)


    @api.depends('name','pay_band_from','pay_band_to')
    def name_get(self):
        res = []
        name = ''
        for rec in self:
            if rec.name and rec.pay_band_from and rec.pay_band_to:
                name = str(rec.name) + '[' + str(rec.pay_band_from) + ' - ' + str(rec.pay_band_to) + ']'
            else:
                name = 'Pay Level'
            res.append((rec.id, name))
        return res

class HrPayLevel(models.Model):
    _name='payslip.pay.level'
    _description ='HR Payroll Py Level'

    name = fields.Char()
    service_level = fields.Integer(string='Service Cell')
    entry_pay = fields.Integer(string='Entry Pay')
    entry_pay_id = fields.Many2one('hr.payslip.paylevel', string='Entry Pay Id')



    @api.depends('entry_pay_id','entry_pay','service_level')
    def name_get(self):
        res = []
        name = ''
        for rec in self:
            if rec.entry_pay_id and rec.service_level:
                name = str(rec.entry_pay_id.name) + '[' + str(rec.entry_pay_id.pay_band_from) + ' - ' + str(rec.entry_pay_id.pay_band_to) + '] ' + '[ Level ' + str(rec.service_level) + ']'
            else:
                name = 'Entry Pay'
            res.append((rec.id, name))
        return res

    @api.constrains('entry_pay')
    def check_constrains(self):
        for rec in self:
            band_from = rec.entry_pay_id.pay_band_from
            band_to = rec.entry_pay_id.pay_band_to
            if not (band_from <= rec.entry_pay <= band_to):
                raise ValidationError(_(f'Entry Pay should be between {band_from} to {band_to}'))