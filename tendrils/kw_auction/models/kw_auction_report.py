from odoo import models, fields, api, tools

class KwAuctionReport(models.Model):
    _name = 'kw_auction_report'
    _auto = False

    auction_duration = fields.Char(string="Auction Duration")
    auction_ref_id = fields.Char(string="Reference ID")
    item_name = fields.Char(string="Item Name")
    item_model = fields.Char(string="Item Model")
    item_configuration = fields.Char(string="Item Configuration")
    fa_code = fields.Char(string="FA Code")
    serial_no = fields.Char(string="Serial No.")
    used_by_id = fields.Many2one('hr.employee', string="Used By")
    reserve_price = fields.Float(string="Auction Price")
    final_bid = fields.Float(string="Final Bid")
    booked_by_id = fields.Many2one('hr.employee', string="Booked By")
    booked_on = fields.Date(string="Booked On")
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('pending_at_auction', 'Pending At Auction'), ('booked', 'Booked'), ('reserved', 'Reserved'), ('pending_for_complete', 'Pending For Complete'), ('completed', 'Completed'), ('rejected', 'Rejected')], string = 'Status')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    select row_number() over() as  id,
                    auction_duration as auction_duration,
                    auction_ref_id as auction_ref_id,
                    item_name as item_name,
                    item_model as item_model,
                    item_configuration as item_configuration,
                    fa_code as fa_code,
                    serial_no as serial_no,
                    used_by_id as used_by_id,
                    reserve_price as reserve_price,
                    final_bid as final_bid,
                    booked_by_id as booked_by_id,
                    booked_on as booked_on,
                    state as state
            from
                    kw_auction
            where
                    state not in ('draft', 'pending_for_complete')
        )
        """
        self.env.cr.execute(query)