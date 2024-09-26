from multiprocessing import managers
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError




class KwBookAuctionWizard(models.TransientModel):
    _name = 'kw_book_auction_wizard'


    def button_auction_book_lots(self):
        auction_date_record = self.env['kw_auction_date_master'].search([], limit=1)
        date_to = auction_date_record.date_to if auction_date_record else False
        current_date = datetime.now().date()

        emp_data = self.env['res.users'].sudo().search([])
        managers = emp_data.filtered(lambda user: user.has_group('kw_auction.kw_auction_IT_head_group') == True)
        store_managers = emp_data.filtered(lambda user: user.has_group('kw_auction.kw_auction_store_manager_group') == True)

        if current_date > date_to:
            auctioned_items = self.env['kw_auction'].search([
                ('state', '=', 'pending_at_auction'),
            ])
            auctioned_items_to_book = auctioned_items.filtered(lambda auction: len(auction.bid_ids) > 0)
            if auctioned_items_to_book:
                for item in auctioned_items_to_book:
                    interested_bids = item.bid_ids.filtered(lambda bid: bid.status == 'interested')
                    if interested_bids:
                        highest_bid = max(interested_bids.mapped('bid_amount'))
                        highest_bidder = interested_bids.filtered(lambda bid: bid.bid_amount == highest_bid)

                        item.write({
                            'state': 'booked',
                            'final_bid': highest_bid,
                            'booked_by_id': highest_bidder.bidder_id.id,
                            'booked_on': datetime.now().date()
                                    })
                        
                        item.action_log_ids.create({
                        'ref_id':item.id,
                        'action_by':self.env.user.name,
                        'action_taken':'Auctioned Item Booked.',
                        'remark':'Auctioned Item Booked.',
                        })
                        
                        mail_template = self.env.ref('kw_auction.auction_booked_mail')
                        mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(store_managers.mapped('email'))).send_mail(item.id, force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                        self.env.user.notify_success(message='Booked Successfully.')

                    else:
                        item.write({
                            'state': 'requested',
                            'bid_ids': [(5, 0, 0)]
                            })

                        item.action_log_ids.create({
                        'ref_id':item.id,
                        'action_by':self.env.user.name,
                        'action_taken':"Requested For Auction.",
                        'remark':"Requested For Auction.",
                            })   
                        mail_template = self.env.ref('kw_auction.auction_request_mail')
                        mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(managers.mapped('email')), email_cc = ','.join(store_managers.mapped('email'))).send_mail(item.id, force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                        self.env.user.notify_info(message='Requested for auction.')
                
                auctioned_items_no_bids = auctioned_items.filtered(lambda auction: len(auction.bid_ids) == 0)
                for item in auctioned_items_no_bids:
                    item.write({
                        'state': 'requested',
                        })
                    
                    item.action_log_ids.create({
                        'ref_id':item.id,
                        'action_by':self.env.user.name,
                        'action_taken':"Requested For Auction.",
                        'remark':"Requested For Auction.",
                        })
                    mail_template = self.env.ref('kw_auction.auction_request_mail')
                    mail_template.with_context(email_from = self.env.user.employee_ids.work_email, email_to = ','.join(managers.mapped('email')), email_cc = ','.join(store_managers.mapped('email'))).send_mail(item.id, force_send=True, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_info(message='Requested for auction.')

        else:
            raise ValidationError("Auction duration has not ended yet. Cannot book lots.")

    