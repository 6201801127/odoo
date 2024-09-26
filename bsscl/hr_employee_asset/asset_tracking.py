import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError
import re



class AssetTracking(models.Model):
    _name = 'asset.tracking'
    _rec_name = 'employee_id'
    _inherit = 'mail.thread'

    number = fields.Char(string='Asset Allocation #')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]))
    # employee_code = fields.Char('Employee Code', related='employee_id.employee_code')
    business_unit = fields.Char(string='Business Unit')
    designation = fields.Many2one('hr.job', string='Designation')
    department = fields.Many2one('hr.department', string='Department')
    role = fields.Many2one('hr.role', string='Role')
    d_o_j = fields.Date(string='Date of Joining')
    creation_date = fields.Datetime(
        string='Creation Date', default=fields.Datetime.now)
    # created_by = fields.Many2one(
    #     'res.users', string='Approved By', default=lambda self: self.env.user)

    created_by = fields.Many2one(
        'res.users', string='Approved By')
    allocation_date = fields.Datetime(string='Allocated Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit For Approval'),
                              ('approve', 'Awaiting Approval'),
                              ('refuse', 'Refuse'),
                              ('confirm', 'Approved'),
                              ('allocated', 'Allocated'),
                              ('cancel', 'Cancelled')],
                             'Status', required=True, copy=False,
                             track_visibility='onchange', default='draft')
    asset_tracking_ids = fields.One2many(
        'asset.asset.line', 'asset_tracking_id', string='Asset')
    cancellation = fields.Text('Cancelled Summary')
    request_date = fields.Datetime(string='Approved Date')
    # requested_by = fields.Many2one(
    #     'res.users', string='Allocated By', default=lambda self: self.env.user)
    
    requested_by = fields.Many2one(
        'res.users', string='Allocated By')
    @api.constrains('cancellation')
    @api.onchange('cancellation')	
    def _onchange_cancellation(self):
        for rec in self:
            if rec.cancellation and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.cancellation)):
                raise ValidationError("Cancellation should be an alphabet")
            
   

    def submit_for_approval(self):
        for record in self:
            if not record.asset_tracking_ids:
                raise ValidationError(_("Please Fill Assets Type"))
            if record.state == 'draft':
                record.state = 'confirm'
                record.created_by = self.env.user
                record.request_date = fields.Datetime.now()

   
    def approve(self):
        for val in self:
            if not all(obj.asset_tracking_ids for obj in self):
                raise UserError("Please Fill Asset Allocation Line")
        for record in self:
            if record.state == 'approve':
                record.state = 'confirm'

   
    def refuse(self):
        self.write({'state': 'cancel'})
        return True

   
    def cancel_allocation(self):
        for value in self:
            if value.cancellation == 0:
                raise UserError('Please enter reason of cancellation')
        else:
            self.write({'state': 'cancel'})
            return True

   
    def confirm_allocation(self):
        self.ensure_one()
        # for val in self.asset_tracking_ids:
            # if not val.asset_id:
            #     raise UserError("Please Fill Asset in Asset Line")
            # val.asset_id.write(
            #     {'state': 'allocated',
            #      'employee_id': val.asset_tracking_id.employee_id.id,
            #      'department_id': val.asset_tracking_id.department.id})
            # self.env['asset.move'].create({
            #     'asset_id': val.asset_id.id,
            #     'date': fields.Datetime.now(),
            #     'employee_id': val.asset_tracking_id.employee_id.id,
            #     'department_id': val.asset_tracking_id.department.id,
            #     'executed_by': self.env.user.id,
            #     'action': 'allocation',
            #     'asset_name': val.asset_id.name,
            #     'asset_serial': val.asset_id.serial,
            #     'asset_number': val.asset_id.asset_number,
            # })
        self.write({'state': 'allocated',
                    'allocation_date': fields.Datetime.now(),
                    'requested_by':self.env.user})
        return True

    @api.model
    def create(self, vals):
        res = {}
        if 'employee_id' in vals:
            employee_id = self.env['hr.employee'].search(
                [('id', '=', vals.get('employee_id'))])
            vals['designation'] = employee_id.job_id.id
            vals['department'] = employee_id.department_id.id
            vals['d_o_j'] = employee_id.transfer_date
        sequence = self.env['ir.sequence'].next_by_code(
            'asset.tracking') or _('New')
        vals['number'] = sequence
        return super(AssetTracking, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        res = {}
        asset_list = []
        if self.employee_id:
            employee = self.employee_id
            res = {
                'designation': employee.job_id.id,
                'department': employee.department_id.id,
                'd_o_j': employee.transfer_date,
            }
        return {'value': res}

   
    def unlink(self):
        """Allows to delete assets in draft,cancel states"""
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(
                    _("Invalid Action!\nCannot delete a Asset which is in state '%s'." % (rec.state)))
        return super(AssetTracking, self).unlink()


class AssetID(models.Model):
    _inherit = 'asset.asset.line'

    asset_tracking_id = fields.Many2one('asset.tracking', String='Asset')


class AssetTrackingChange(models.Model):
    _name = 'asset.tracking.change'
    _rec_name = 'employee_id'
    _inherit = 'mail.thread'

    number_change = fields.Char(string='Asset Change #')
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]))
    employee_code = fields.Char(string='Employee Code')
    business_unit = fields.Char(string='Business Unit')
    designation = fields.Many2one(
        'hr.job', string='Designation', readonly=True)
    department = fields.Many2one(
        'hr.department', string='Department', readonly=True)
    role = fields.Many2one('hr.role', string='Role')
    date_of_join = fields.Date(string='Date of Joining', readonly=True)
    creation_date = fields.Datetime(
        string='Creation Date', default=fields.Datetime.now)
    created_by = fields.Many2one(
        'res.users', string='Created By', default=lambda self: self.env.user)
    allocation_date = fields.Datetime(
        string='Change/ Return Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit For Approval'),
                              ('approve', 'Awaiting Approval'),
                              ('refuse', 'Refuse'),
                              ('allocated', 'Change/Return'),
                              ('confirm', 'Approved'),
                              ('cancel', 'Cancelled')],
                             'Status', required=True, copy=False,
                             track_visibility='onchange', default='draft')
    asset_change_ids = fields.One2many(
        'asset.tracking.line.change', 'current_id', string='Asset')
    cancellation = fields.Text('Cancelled Summary')
    request_date = fields.Datetime(string='Request Date')
    requested_by = fields.Many2one(
        'res.users', string='Requested By', default=lambda self: self.env.user)

   
    def submit_for_approval(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'approve'
                record.request_date = fields.Datetime.now()
            asset_state = self.env['asset.tracking.line.change'].search(
                [('current_id', '=', self.id)])
            asset_state.write({'state': self.state})
            return True

   
    def approve(self):
        for val in self:
            if not all(obj.asset_change_ids for obj in self):
                raise UserError("Please Fill Asset Change Line")
        for record in self:
            if record.state == 'approve':
                record.state = 'confirm'
            asset_state = self.env['asset.tracking.line.change'].search(
                [('current_id', '=', self.id)])
            asset_state.write({'state': self.state})

   
    def refuse(self):
        self.write({'state': 'refuse'})
        asset_state = self.env['asset.tracking.line.change'].search(
            [('current_id', '=', self.id)])
        asset_state.write({'state': self.state})
        return True

   
    def cancel_asset_change(self):
        for value in self:
            if value.cancellation == 0:
                raise UserError('Please enter reason of cancellation')
        else:
            self.write({'state': 'cancel'})
            asset_state = self.env['asset.tracking.line.change'].search(
                [('current_id', '=', self.id)])
            asset_state.write({'state': self.state})
            return True

   
    def confirm_asset_change(self):
        current_date = fields.Datetime.now()
        for asset in self.asset_change_ids:
            dic_1 = {
                'asset_id': asset.current_assets_id.id,
                'date': current_date,
                'employee_id': asset.current_id.employee_id.id,
                'executed_by': self.env.user.id,
                'action': 'change',
                'department_id': asset.current_id.department.id,
                'asset_name': asset.current_assets_id.name,
                'asset_serial': asset.current_assets_id.serial,
                'asset_number': asset.current_assets_id.asset_number,
            }
            asset.current_assets_id.write(
                {'state': 'hold', 'employee_id': None,
                 'department_id': None})
            self.env['asset.move'].create(dic_1)
            dic_2 = {
                'asset_id': asset.asset_name.id,
                'date': current_date,
                'employee_id': asset.current_id.employee_id.id,
                'executed_by': self.env.user.id,
                'action': 'allocation',
                'department_id': asset.current_id.department.id,
                'asset_name': asset.asset_name.name,
                'asset_serial': asset.asset_name.serial,
                'asset_number': asset.asset_name.asset_number,
            }
            asset.asset_name.write(
                {'state': 'allocated',
                 'employee_id': self.employee_id.id,
                 'department_id': self.department.id})
            self.env['asset.move'].create(dic_2)
        self.write(
            {'state': 'allocated', 'allocation_date': current_date})
        asset_state = self.env['asset.tracking.line.change'].search(
            [('current_id', '=', self.id)])
        asset_state.write({'state': self.state})
        return True

    @api.model
    def create(self, vals):
        if 'employee_id' in vals:
            employee_id = self.env['hr.employee'].search(
                [('id', '=', vals.get('employee_id'))])
            vals['designation'] = employee_id.job_id.id
            vals['department'] = employee_id.department_id.id
        sequence = self.env['ir.sequence'].next_by_code(
            'asset.tracking.change') or _('New')
        vals['number_change'] = sequence
        res = super(AssetTrackingChange, self).create(vals)
        return res

   
    @api.onchange("employee_id")
    def onchange_employee_id(self):
        res = {}
        if self.employee_id:
            employee = self.env['hr.employee']
            asset_obj = self.env['asset.asset']
            asset_ids = asset_obj.search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'allocated')])
            res = {
                'designation': self.employee_id.job_id.id,
                'department': self.employee_id.department_id.id,
                'date_of_join': self.employee_id.transfer_date,
            }
            asset_list = []
            for asset in asset_obj.browse(asset_ids):
                asset_list.append((0, 0,
                                   {'current_assets_id': asset.id}))
            res['asset_change_ids'] = asset_list
        return {'value': res}

   
    def unlink(self):
        """Allows to delete assets in draft,cancel states"""
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(
                    _("Invalid Action!\nCannot delete a Asset which is in state '%s'." % (rec.state)))
        return super(AssetTrackingChange, self).unlink()


class AssetTrackingLineChange(models.Model):
    _name = 'asset.tracking.line.change'
    _rec_name = 'asset_name'

    current_id = fields.Many2one('asset.tracking.change', String='Asset')
    asset_name = fields.Many2one('asset.asset', string='New Asset')
    reason = fields.Char(string='Reason For Change/Return')
    remarks = fields.Char(string='Remarks')
    action = fields.Selection(
        [('change', 'Changed')], 'Action', readonly=True, copy=False,
        default='change')
    current_assets_id = fields.Many2one(
        'asset.asset', 'Current Asset', required=True)
    service_area_id = fields.Many2one(
        'hr.employee.service.area', string="Service Area")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit For Approval'),
                              ('approve', 'Awaiting Approval'),
                              ('refuse', 'Refuse'),
                              ('allocated', 'Allocated'),
                              ('confirm', 'Approved'),
                              ('cancel', 'Cancelled')],
                             'Status',
                             track_visibility='onchange', default='draft')
