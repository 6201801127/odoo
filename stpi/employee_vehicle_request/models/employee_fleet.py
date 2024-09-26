# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class FleetReservedTime(models.Model):
    _name = "fleet.reserved"
    _description = "Reserved Time"
    
    
    employee = fields.Many2one('hr.employee', string='Requested By')
    date_from = fields.Datetime(string='Reserved Date From')
    date_to = fields.Datetime(string='Reserved Date To')
    reserved_obj = fields.Many2one('fleet.vehicle')


class FleetVehicleInherit(models.Model):
    _inherit = 'fleet.vehicle'

    check_availability = fields.Boolean(default=True, copy=False)
    reserved_time = fields.One2many('fleet.reserved', 'reserved_obj', String='Reserved Time', readonly=1,
                                    ondelete='cascade')


class EmployeeFleet(models.Model):
    _name = 'employee.fleet'
    _description = 'Employee Vehicle Request'
    _inherit = ['mail.thread','mail.activity.mixin']

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.fleet')
        return super(EmployeeFleet, self).create(vals)

    @api.multi
    def send(self):
        # fleet_obj = self.env['fleet.vehicle'].search([])
        # check_availability = 0
        # self.remark_date_to = datetime.now()
        # for i in fleet_obj:
        #     for each in i.reserved_time:
        #         if each.date_from <= self.date_from <= each.date_to:
        #             check_availability = 1
        #         elif self.date_from < each.date_from:
        #             if each.date_from <= self.date_to <= each.date_to:
        #                 check_availability = 1
        #             elif self.date_to > each.date_to:
        #                 check_availability = 1
        #             else:
        #                 check_availability = 0
        #         else:
        #             check_availability = 0
        # if check_availability == 0:
        #     reserved_id = self.fleet.reserved_time.create({'employee': self.employee.id,
        #                                                    'date_from': self.date_from,
        #                                                    'date_to': self.date_to,
        #                                                    'reserved_obj': self.fleet.id,
        #                                                    })
        #     self.write({'reserved_fleet_id': reserved_id.id})
        self.state = 'waiting'
        # else:
        #     raise Warning('Sorry This vehicle is already requested by another employee')

        if self.employee.user_id:
            self.activity_schedule(summary='Vahical Request', activity_type_id=4,
                                   date_deadline=datetime.now().date(),
                                   user_id=self.employee.user_id.id,
                                   )
        else:
            self.activity_schedule(summary='Vahical Request', activity_type_id=4,
                                   date_deadline=datetime.now().date(),
                                   user_id=self.env.user.id,
                                   )
    #
    # @api.multi
    # def button_forwarded(self):
    #     for rec in self:
    #         rec.write({'state': 'forwarded'})


    @api.multi
    def approve(self):
        self.fleet.fleet_status = True
        self.state = 'confirm'
        mail_content = _('Hi %s,<br>Your vehicle request for the reference %s is approved.') % \
                        (self.employee.name, self.name)
        main_content = {
            'subject': _('%s: Approved') % self.name,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': self.employee.work_email,
        }
        mail_id = self.env['mail.mail'].create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.send()
        if self.employee.user_id:
            mail_id.mail_message_id.write({'needaction_partner_ids': [(4, self.employee.user_id.partner_id.id)]})
            mail_id.mail_message_id.write({'partner_ids': [(4, self.employee.user_id.partner_id.id)]})

        self.activity_feedback(['employee_vehicle_request.mail_employee_approval'], user_id=self.env.user.id,
                               feedback='Approved'+str(datetime.now()))
        self.all_activity_unlinks()

    # @api.multi
    # def button_processed(self):
    #     for rec in self:
    #         rec.write({'state': 'processed'})


    @api.multi
    def unlink(self):
        for fleets in self:
            if fleets.state != 'draft':
                raise UserError(
                    'You cannot delete a Request which is not in draft state')
        return super(EmployeeFleet, self).unlink()

    @api.multi
    def reject(self):
        self.reserved_fleet_id.unlink()
        self.state = 'reject'
        mail_content = _('Hi %s,<br>Sorry, Your vehicle request for the reference %s is Rejected.') % \
                        (self.employee.name, self.name)

        main_content = {
            'subject': _('%s: Approved') % self.name,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': self.employee.work_email,
        }
        mail_id = self.env['mail.mail'].create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.send()
        if self.employee.user_id:
            mail_id.mail_message_id.write({'needaction_partner_ids': [(4, self.employee.user_id.partner_id.id)]})
            mail_id.mail_message_id.write({'partner_ids': [(4, self.employee.user_id.partner_id.id)]})

        self.activity_feedback(['employee_vehicle_request.mail_employee_approval'], user_id=self.env.user.id,
                               feedback='Rejected'+str(datetime.now()))
        self.all_activity_unlinks()

    @api.multi
    def cancel(self):
        if self.reserved_fleet_id:
            self.reserved_fleet_id.unlink()
        self.state = 'cancel'
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,

            default_model='employee.fleet',
            default_is_log='True',
            custom_layout='mail.mail_notification_light'
        )
        mw = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        self.write({'state': 'draft'})
        return mw


    @api.multi
    def returned(self):
        self.reserved_fleet_id.unlink()
        self.returned_date = fields.datetime.now()
        self.state = 'return'

    # @api.constrains('date_rom', 'date_to')
    # def onchange_date_to(self):
    #     for each in self:
    #         if each.date_from > each.date_to:
    #             raise Warning('Date To must be greater than Date From')
    #
    # @api.onchange('date_from', 'date_to')
    # def check_availability(self):
    #     if self.date_from and self.date_to:
    #         self.fleet = ''
    #         fleet_obj = self.env['fleet.vehicle'].search([])
    #         for i in fleet_obj:
    #             for each in i.reserved_time:
    #                 if each.date_from <= self.date_from <= each.date_to:
    #                     i.write({'check_availability': False})
    #                 elif self.date_from < each.date_from:
    #                     if each.date_from <= self.date_to <= each.date_to:
    #                         i.write({'check_availability': False})
    #                     elif self.date_to > each.date_to:
    #                         i.write({'check_availability': False})
    #                     else:
    #                         i.write({'check_availability': True})
    #                 else:
    #                     i.write({'check_availability': True})


    def activity_feedback(self, act_type_xmlids, user_id=None, feedback=None):
        """ Set activities as done, limiting to some activity types and
        optionally to a given user. """
        if self.env.context.get('mail_activity_automation_skip'):
            return False

        # print("--------------------------act_type_xmlids",act_type_xmlids)
        Data = self.env['ir.model.data'].sudo()
        activity_types_ids = [Data.xmlid_to_res_id(xmlid) for xmlid in act_type_xmlids]
        domain = [
            '&', '&', '&',
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('automated', '=', True),
            ('activity_type_id', 'in', [4])
        ]
        if user_id:
            domain = ['&'] + domain + [('user_id', '=', user_id)]
        activities = self.env['mail.activity'].search(domain)
        if activities:
            activities.action_feedback(feedback=feedback)
        return True

    def all_activity_unlinks(self):
        if self:
            # print("------------------all_activity_unlinks")
            domain = [
                '&', '&', '&',
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('automated', '=', True),
                ('activity_type_id', '=', 4)
            ]
            activities = self.env['mail.activity'].search(domain)
            for activity in activities:
                activity.unlink()

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    reserved_fleet_id = fields.Many2one('fleet.reserved', invisible=1, copy=False)
    name = fields.Char(string='Request Number', copy=False)
    employee = fields.Many2one('hr.employee', string='Requested By', required=1, readonly=True,default=_default_employee)
    branch_id= fields.Many2one('res.branch', string="Center", compute='compute_des_dep',store=True)
    department_id = fields.Many2one('hr.department','Department',track_visibility='onchange')
    req_date = fields.Date(string='Requested Date', default=datetime.now().date(), required=1, readonly=True,help="Requested Date")
    fleet = fields.Many2one('fleet.vehicle', string='Vehicle', help="only available vehicles are being displayed. No results >>> No vehicle avaiable",
                            )
    date_from = fields.Datetime(string='From')
    date_to = fields.Datetime(string='To')
    requested_date = fields.Date(string='Requested Date')
    half_day = fields.Boolean(string='Half Day')
    driver_name = fields.Char(string='Driver Name')
    agency_id = fields.Many2one('agency.details', string='Agency')
    driver_mobile = fields.Char(string='Driver Mobile')
    returned_date = fields.Datetime(string='Returned Date', readonly=1)
    purpose = fields.Text(string='Purpose', required=1, readonly=True,track_visibility='always',
                          states={'draft': [('readonly', False)]}, help="Purpose")
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('cancel', 'Cancel'),
                              ('confirm', 'Approved'), ('reject', 'Rejected'), ('return', 'Returned')],
                             string="State", default="draft")
    # state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('forwarded', 'Forwarded'), ('cancel', 'Cancel'), ('confirm', 'Approved'), ('processed', 'Processed'), ('reject', 'Rejected'), ('return', 'Returned')],
    #     string="State", default="draft")
    from_location = fields.Char(string="From Location",required=True,track_visibility='always')
    to_location = fields.Char(string="To Location",required=True,track_visibility='always')
    via = fields.Char(string='Via',track_visibility='always')
    remark = fields.Text(string='Remark',track_visibility='always')
    remark_date_to = fields.Datetime(string='Send for approval current date', track_visibility='always')

    created_by = fields.Many2one('res.users', 'Created By',default=lambda self: self.env.user,track_visibility='always')
    driver_id = fields.Many2one('res.partner', 'Driver',track_visibility='always')

    @api.constrains('employee')
    @api.onchange('employee')
    def compute_des_dep(self):
        for rec in self:
            rec.department_id = rec.employee.department_id.id
#             print("??????????????????????",rec.department_id)
            rec.branch_id = rec.employee.branch_id.id


    @api.onchange('fleet')
    def get_driver(self):
        for s in self:
            if self.fleet.driver_id:
                s.driver_id = self.fleet.driver_id.id


class AgencyDetails(models.Model):
    _name = 'agency.details'
    _description = 'Agency Details'

    name = fields.Char(string='Name')
    phone = fields.Char()
    address = fields.Char(string='Address')