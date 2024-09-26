# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.http import request

class KwAuction(models.Model):
    _name = 'kw_auction'
    _rec_name = 'auction_ref_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Auction'

    auction_ref_id = fields.Char(string="Reference ID", readonly = True, copy=False, default='New', track_visibility='onchange')
    item_name = fields.Char(string="Item Name", track_visibility='onchange')
    item_model = fields.Char(string="Item Model", track_visibility='onchange')
    item_configuration = fields.Char(string="Item Configuration", track_visibility='onchange')
    fa_code = fields.Char(string="FA Code", track_visibility='onchange')
    serial_no = fields.Char(string="Serial No.", track_visibility='onchange')
    used_by_id = fields.Many2one('hr.employee', string="Used By", track_visibility='onchange')
    description = fields.Text(string="Description", track_visibility='onchange')
    reserve_price = fields.Float(string="Reserve Price", track_visibility='onchange')
    highest_bid = fields.Float(string="Highest Bid", compute="_compute_highest_bid", track_visibility='onchange')
    booked_by_id = fields.Many2one('hr.employee', string="Booked By", track_visibility='onchange')
    booked_on = fields.Date(string="Booked On", track_visibility='onchange')
    final_bid = fields.Float(string="Final Bid", track_visibility='onchange')
    item_photo_ids = fields.One2many('kw_auction_item_photo_master', 'auction_id', string='Photos', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('pending_at_auction', 'Pending At Auction'), ('booked', 'Booked'), ('reserved', 'Reserved'), ('pending_for_complete', 'Pending For Complete'), ('completed', 'Completed'), ('rejected', 'Rejected')], string = 'Status', default = 'draft', track_visibility='onchange')
    auction_duration = fields.Char(string="Auction Duration", track_visibility='onchange')
    bid_ids = fields.One2many('kw_auction_bids', 'ref_id', string='Bids', track_visibility='onchange')
    action_log_ids = fields.One2many('kw_auction_action_log', 'ref_id', string='Action Log', track_visibility='onchange')
    pending_at_ids = fields.Many2many('hr.employee', string='Pending At', compute='get_pending_at', track_visibility='onchange')
    auction_request_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    auction_reserve_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    auction_request_approve_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    auction_request_reject_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    bid_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    release_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    request_to_complete_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    complete_button_show_hide_boolean = fields.Boolean(compute="check_button_access")
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)


    @api.constrains('reserve_price')
    def _check_reserve_price(self):
        if self.reserve_price <= 0:
            raise ValidationError("Reserve price can not be less that or equal to 0.")


    @api.depends('bid_ids')
    def _compute_highest_bid(self):
        for rec in self:
            if rec.bid_ids:
                rec.highest_bid = max(rec.bid_ids.mapped('bid_amount'))
            else:
                rec.highest_bid = 0.0


    @api.depends('state')
    def _compute_css(self):
        context = self._context or {}
        for rec in self:
            if (rec.state in ['draft', 'requested'] and context.get('add') and self.env.user.has_group('kw_auction.kw_auction_store_manager_group')) or (rec.state in ['requested'] and context.get('manager_take_action') and self.env.user.has_group('kw_auction.kw_auction_IT_head_group')):
                rec.test_css = ''
            else:
                rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'


    @api.depends('state')
    def check_button_access(self):
        context = self._context or {}
        for rec in self:
            rec.auction_request_button_show_hide_boolean = True if context.get('add') and rec.state in ['draft'] else False
            rec.auction_reserve_button_show_hide_boolean = True if context.get('manager_take_action') and rec.state in ['requested'] else False
            rec.auction_request_approve_button_show_hide_boolean = True if context.get('manager_take_action') and rec.state in ['requested'] else False
            rec.auction_request_reject_button_show_hide_boolean = True if context.get('manager_take_action') and rec.state in ['requested'] else False
            auction_date_record = self.env['kw_auction_date_master'].search([], limit=1)
            date_from = auction_date_record.date_from
            date_to = auction_date_record.date_to
            current_date = datetime.now().date()
            if context.get('view') and rec.state == 'pending_at_auction' and (date_from <= current_date and current_date <= date_to):
                existing_bid = self.env['kw_auction_bids'].search([('ref_id', '=', rec.id), ('bidder_id', '=', self.env.user.employee_ids.id)], limit=1)
                rec.bid_button_show_hide_boolean = not existing_bid
            rec.release_button_show_hide_boolean = True if context.get('store_manager_take_action') and rec.state in ['booked', 'reserved'] else False
            rec.request_to_complete_button_show_hide_boolean = True if context.get('store_manager_take_action') and rec.state in ['booked', 'reserved'] else False
            rec.complete_button_show_hide_boolean = True if context.get('manager_take_action') and rec.state in ['pending_for_complete'] else False
    

    @api.model
    def create(self, vals):
        vals['auction_ref_id'] = vals['item_name'] + '/' + vals['item_model'] + '/' + self.env['ir.sequence'].next_by_code('KwAuction.sequence') or '/'
        return super(KwAuction, self).create(vals)
   
    
    def get_pending_at(self):
        managers = self.env['res.users'].sudo().search([]).filtered(lambda user: user.has_group('kw_auction.kw_auction_IT_head_group') == True)
        store_managers = self.env['res.users'].sudo().search([]).filtered(lambda user: user.has_group('kw_auction.kw_auction_store_manager_group') == True)
        for rec in self:
            employee_ids = []
            if rec.state in ['requested', 'pending_for_complete']:
                employee_ids.extend(managers.mapped('employee_ids').ids) if managers else False
            elif rec.state in ['booked', 'reserved']:
                employee_ids.extend(store_managers.mapped('employee_ids').ids) if store_managers else False
            rec.pending_at_ids = [(6, 0, employee_ids)] if employee_ids else False
    

    def button_auction_open_request(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'requested', 'action_taken':'Requested For Auction.', 'booked_by':False, 'booked_on':False, 'final_bid':False}
            }
    
    def button_auction_open_approve(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'pending_at_auction', 'action_taken':'Opened For Auction.', 'booked_by':False, 'booked_on':False, 'final_bid':False}
            }
    
    def button_auction_request_reject(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'rejected', 'action_taken':'Rejected.', 'booked_by':False, 'booked_on':False, 'final_bid':False}
            }
    
    def button_auction_reserve(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'reserved', 'action_taken':'Reserved.', 'booked_by':False, 'booked_on':datetime.now().date(), 'final_bid':False}
            }


    def button_auction_bid(self):
        view_id = self.env.ref('kw_auction.kw_auction_it_declaration_form').id
        return {
                'name':"Bid",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_it_declaration',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'create':False}
            }

    def button_auction_release(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'requested', 'action_taken':'Auctioned Item Released.', 'booked_by':False, 'booked_on':False, 'final_bid':False, 'booked_by_id': self.booked_by_id.id}
            }
    
    def button_auction_request_to_completed(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'pending_for_complete', 'action_taken':'Requested To Complete Auction.', 'booked_by':self.booked_by_id.id, 'booked_on':self.booked_on, 'final_bid':self.final_bid}
            }

    def button_auction_completed(self):
        view_id = self.env.ref('kw_auction.kw_auction_remark_wizard_form').id
        return {
                'name':"Remark",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_remark_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id, 'state':'completed', 'action_taken':'Auction Completed.', 'booked_by':self.booked_by_id.id, 'booked_on':self.booked_on, 'final_bid':self.final_bid}
            }
    
    
    def get_upload_images(self):
        for rec in self:
            view_id = self.env.ref('kw_auction.kw_auction_item_photo_upload_wizard_form').id
            return {
                'name': 'Upload Images',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_auction_item_photo_upload_wizard',
                'target': 'new',
                'context':{
                'default_auction_id': rec.id
                }
            }
        

    def get_auction_records(self):
        auction_date_record = self.env['kw_auction_date_master'].search([], limit=1)
        if auction_date_record:
            date_from = auction_date_record.date_from
            date_to = auction_date_record.date_to
            current_date = datetime.now().date()

            if date_from <= current_date and current_date <= date_to:
                domain = [('state','in',['pending_at_auction'])]
            else:
                domain = [('state','in',[])]
        else:
                domain = [('state','in',[])]

        tree_view_id = self.env.ref('kw_auction.kw_auction_list').id
        form_view_id = self.env.ref('kw_auction.kw_auction_form').id
        search_view_id = self.env.ref('kw_auction.kw_auction_search').id

        group_by_default = 'item_name'

        action = {'type': 'ir.actions.act_window',
                'name': 'View Auctions',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (search_view_id, 'search')],
                'view_mode': 'tree,form,search',
                'res_model': 'kw_auction',
                'domain': domain,
                'context': {'create': False, 'delete': False, 'copy': False, 'view': True, 'group_by': group_by_default},
                'help': '<p class="o_view_nocontent_smiling_face">No items are currently up for auction...</p>'
                }
        return action
    

    def take_action(self):
        if self.env.user.has_group('kw_auction.kw_auction_store_manager_group'):
            domain = [('state', 'in', ['booked','reserved'])]
            context = {'create': False, 'delete': False, 'copy': False, 'store_manager_take_action':1, 'search_default_filter_my_bookings':1}
        elif self.env.user.has_group('kw_auction.kw_auction_IT_head_group'):
            domain = [('state', 'not in', ['draft'])]
            context = {'create': False, 'delete': False, 'copy': False, 'manager_take_action':1, 'search_default_filter_to_take_action':1}
        else:
            domain = []
            context = {}

        tree_view_id = self.env.ref('kw_auction.kw_auction_list').id
        form_view_id = self.env.ref('kw_auction.kw_auction_form').id
        search_view_id = self.env.ref('kw_auction.kw_auction_search').id

        action = {'type': 'ir.actions.act_window',
                'name': 'Take Action',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (search_view_id, 'search')],
                'view_mode': 'tree,form,search',
                'res_model': 'kw_auction',
                'domain': domain,
                'context': context,
                'help': '<p class="o_view_nocontent_smiling_face">There are no records awaiting for approval...</p>'
                }
        return action   
    

    def view_my_bids(self):
        bids = self.env['kw_auction_bids'].search([('bidder_id.id', '=', self.env.user.employee_ids.id)])
        my_bid_ids = [bid.ref_id.id for bid in bids if bid.ref_id.state == 'pending_at_auction']

        domain = [('id', 'in', my_bid_ids)]
        
        tree_view_id = self.env.ref('kw_auction.kw_auction_list').id
        form_view_id = self.env.ref('kw_auction.kw_auction_form').id

        action = {
            'type': 'ir.actions.act_window',
            'name': 'My Bids',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'res_model': 'kw_auction',
            'domain': domain,
            'context': {'create': False, 'delete': False, 'copy': False, 'my_bids': 1},
            'help': '<p class="o_view_nocontent_smiling_face">You have not placed any bids yet...</p>'
        }
        return action 
    

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(('You cannot duplicate a record.'))
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('You have no access to delete this record.')
        return super(KwAuction, self).unlink()
    

class KwAuctionBids(models.Model):
    _name = 'kw_auction_bids'
    _order = 'bid_amount desc'

    ref_id = fields.Many2one('kw_auction')
    bidder_id = fields.Many2one('hr.employee', string="Bidder")
    bid_amount = fields.Float(string="Bid Amount")
    date = fields.Date(string="Date", default = fields.date.today())
    status = fields.Selection([('interested', 'Interested'), ('withdrawn_interest', 'Withdrawn Interest')], string = 'Status')
    rebid_withdraw_interest_button_show_hide_boolean = fields.Boolean(compute = "check_button_access")


    def button_auction_withdraw_interest(self):
        self.status = 'withdrawn_interest'


    @api.depends('status')
    def check_button_access(self):
        context = self._context or {}
        auction_date_record = self.env['kw_auction_date_master'].search([], limit=1)
        date_from = auction_date_record.date_from
        date_to = auction_date_record.date_to
        current_date = datetime.now().date()
        for rec in self:
            rec.rebid_withdraw_interest_button_show_hide_boolean = True if rec.bidder_id.id == self.env.user.employee_ids.id and rec.status == 'interested' and rec.ref_id.state == "pending_at_auction"  and (date_from <= current_date and current_date <= date_to) and (context.get('view') or context.get('my_bids')) else False


    def button_auction_rebid(self):
        view_id = self.env.ref('kw_auction.kw_auction_rebid_wizard_form').id
        return {
                'name':"Rebid",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'kw_auction_rebid_wizard',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'current_id': self.id}
            }



class KwAuctionRebid(models.TransientModel):
    _name = 'kw_auction_rebid_wizard'
 
    ref_id = fields.Many2one('kw_auction_bids', default= lambda self:self.env.context.get('current_id'))
    rebid_amount = fields.Float(string="Rebid Amount")

    
    def proceed_rebid(self):
        if self.rebid_amount >= self.ref_id.bid_amount:
            active_id = self.env.context.get('active_id')
            model_data = self.env['kw_auction_bids'].search([('id','=',active_id)])
            model_data.write({
                    'bid_amount': self.rebid_amount,
                    'date': datetime.now().date()
                })
        else:
            raise ValidationError("The rebid amount must be greater than the current bid amount.")


class KwAuctionActionLog(models.Model):
    _name = 'kw_auction_action_log'

    ref_id = fields.Many2one('kw_auction')
    date = fields.Date(string="Date", default = fields.date.today())
    action_by = fields.Char(string="Action Taken By")
    action_taken = fields.Char(string="Action Taken")
    remark = fields.Text(string="Remark")


class KwAuctionRemarkWizard(models.TransientModel):
    _name = 'kw_auction_remark_wizard'

    @api.model
    def default_get(self, fields):
        res = super(KwAuctionRemarkWizard, self).default_get(fields)
        auction_ids = self._context.get('active_ids')
        draft_auction_ids = self.env['kw_auction'].search([('id', 'in', auction_ids), ('state', '=', 'draft')]).ids
        res.update({
            'ref_ids': draft_auction_ids,
        })
        return res
    
    ref_id = fields.Many2one('kw_auction', default= lambda self:self.env.context.get('current_id'))
    ref_ids = fields.Many2many('kw_auction', string='Auction References', readonly=True)
    reserve_for_id = fields.Many2one('hr.employee', string="Reserve For")
    remarks = fields.Text(string="Remark", required=True)
    ref_ids_show_hide_bool = fields.Boolean(compute='compute_ref_ids_show_hide_bool')
    reserve_for_id_show_hide_bool = fields.Boolean(compute='compute_reserve_for_id_show_hide_bool')


    @api.depends('ref_id')
    def compute_ref_ids_show_hide_bool(self):
        if self.ref_id:
            self.ref_ids_show_hide_bool = True


    @api.depends('ref_id')
    def compute_reserve_for_id_show_hide_bool(self):
        if self.ref_id and self.env.context.get('action_taken') == 'Reserved.':
            self.reserve_for_id_show_hide_bool = True


    def proceed_with_remark(self):
        emp_data = self.env['res.users'].sudo().search([])
        managers = emp_data.filtered(lambda user: user.has_group('kw_auction.kw_auction_IT_head_group') == True)
        store_managers = emp_data.filtered(lambda user: user.has_group('kw_auction.kw_auction_store_manager_group') == True)

        date_master = self.env['kw_auction_date_master'].search([], limit=1)

        if self.env.context.get('current_id'):
            active_id = self.env.context.get('active_id')
            model_data = self.env['kw_auction'].search([('id','=',active_id)])
            model_data.write({
                    'state': self.env.context.get('state'),
                    'booked_by_id': self.reserve_for_id.id if self.reserve_for_id else self.env.context.get('booked_by'),
                    'booked_on': self.env.context.get('booked_on'),
                    'final_bid': self.env.context.get('final_bid'),
                    'bid_ids': [(5, 0, 0)] if self.env.context.get('action_taken') == 'Auctioned Item Released.' else None
                })
            
            self.ref_id.action_log_ids.create({
            'ref_id':self.env.context.get('current_id'),
            'action_by':self.env.user.name,
            'action_taken':self.env.context.get('action_taken'),
            'remark':self.remarks,
            })

            if self.env.context.get('action_taken') == 'Requested For Auction.':
                mail_template = self.env.ref('kw_auction.auction_request_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(managers.mapped('email')), email_cc = ','.join(store_managers.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'), force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_info(message='Requested for auction.')
            elif self.env.context.get('action_taken') == 'Auctioned Item Released.':
                previous_booked_by_id = self.env['hr.employee'].browse(self.env.context.get('booked_by_id'))
                mail_template = self.env.ref('kw_auction.auction_released_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = previous_booked_by_id.work_email, email_cc = ','.join(managers.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_info(message='Auctioned item released.')
            elif self.env.context.get('action_taken') == 'Requested To Complete Auction.':
                mail_template = self.env.ref('kw_auction.auction_request_to_complete_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(managers.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_info(message='Requested to complete auction.')
            elif self.env.context.get('action_taken') == 'Auction Completed.':
                mail_template = self.env.ref('kw_auction.auction_completed_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_cc = ','.join(store_managers.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'),force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success(message='Auction completed.')
            elif self.env.context.get('action_taken') == 'Reserved.':
                mail_template = self.env.ref('kw_auction.auction_reserved_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_cc = ','.join(store_managers.mapped('email')), remark=self.remarks).send_mail(self.env.context.get('active_id'), force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                model_data.write({
                    'auction_duration' : f"{date_master.date_from.strftime('%d-%b-%Y')} to {date_master.date_to.strftime('%d-%b-%Y')}"
                })
                self.env.user.notify_info(message='Reserved.')
            elif self.env.context.get('action_taken') == 'Opened For Auction.':
                model_data.write({
                    'auction_duration' : f"{date_master.date_from.strftime('%d-%b-%Y')} to {date_master.date_to.strftime('%d-%b-%Y')}"
                })
                self.env.user.notify_success(message='Approved and opened for auction.')
            elif self.env.context.get('action_taken') == 'Rejected.':
                model_data.write({
                    'auction_duration' : f"{date_master.date_from.strftime('%d-%b-%Y')} to {date_master.date_to.strftime('%d-%b-%Y')}"
                })
                self.env.user.notify_danger(message='Rejected.')
        else:
            if len(self.ref_ids) != 0:
                self.ref_ids.write({
                        'state': 'requested'
                    })
                
                auction_references = ''
                for auction_id in self.ref_ids:
                    auction_id.action_log_ids.create({
                        'ref_id':auction_id.id,
                        'action_by':self.env.user.name,
                        'action_taken':'Requested For Auction.',
                        'remark':self.remarks,
                        })
                    
                    auction_references += f'{auction_id.auction_ref_id}, '
                    
                mail_template = self.env.ref('kw_auction.multiple_auction_request_mail')
                mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(managers.mapped('email')), email_cc = ','.join(store_managers.mapped('email')), auction_ref = auction_references, remark=self.remarks).send_mail(self.env.context.get('active_id'), force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_info(message='Requested for auction.')
            else:
                raise ValidationError("No record found to Request for auction.\nOr, \nIt seems you're attempting this operation in a incompatible menu. This operation is only available in the 'Add' menu.")
        


class KwAuctionItemPhotoMaster(models.Model):
    _name = 'kw_auction_item_photo_master'

    auction_id = fields.Many2one('kw_auction', string = 'Auction_id')
    photo = fields.Binary(string = 'Photo', attachment = 'True')
    auction_state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('pending_at_auction', 'Pending At Auction'), ('booked', 'Booked'), ('reserved', 'Reserved'), ('pending_for_complete', 'Pending For Complete'), ('completed', 'Completed'), ('rejected', 'Rejected')], string = 'Auction State', related='auction_id.state')


    def remove_upload_images(self):
        return self.unlink()

    def action_download_image(self):
        # Redirect to the controller route
        return {
            'type': 'ir.actions.act_url',
            'url': '/download/image/%s' % self.id,
            'target': 'self',
        }

class KwAuctionItemPhotoUploadWizard(models.TransientModel):
    _name = 'kw_auction_item_photo_upload_wizard'
    _description = 'Upload Multiple Images'
    
    photos_ids = fields.Many2many('ir.attachment', string='Images')
    auction_id = fields.Many2one('kw_auction')
    

    @api.constrains('photos_ids')
    def _check_image_size(self):
        for image in self.photos_ids:
            if image.file_size > 1024 * 1024:
                raise ValidationError("Image '{}' exceeds the maximum allowed size of 1 MB.".format(image.name))
    

    def upload_image(self):
        for rec in self.photos_ids:
            self.auction_id = self.env.context.get('default_auction_id')
            if self.auction_id:
                self.auction_id.item_photo_ids.create({
                    'auction_id': self.auction_id.id,
                    'photo':rec.datas,
                })