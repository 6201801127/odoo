import string
from odoo import models, fields, api, _

class RenewDateAssignWizard(models.TransientModel):
    _name = "renew_date_assign_wizard"
    _description = "Renew Date Assign Wizard"

    mr_dt = fields.Date('Maturity Date')
    fd_id = fields.Many2one('fd_tracker')


    @api.multi
    def action_assign_renew_date(self):
        fd = self.env['fd_tracker'].browse(self.env.context.get('active_id'))
    
        
        for rec in fd:
            rec.ensure_one()
            rec.state = 'renewed'
            new_fd_record = rec.copy(default={})

            current_serial = rec.serial_no
            letter_dict = {'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': 'G', 'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'K': 'L', 'L': 'M', 'M': 'N', 'N': 'O', 'O': 'P', 'P': 'Q', 'Q': 'R', 'R': 'S', 'S': 'T', 'T': 'U', 'U': 'V', 'V': 'W', 'W': 'X', 'X': 'Y', 'Y': 'Z'}
            if current_serial[-1].isnumeric():
                rec.serial_no = f"{current_serial}A"
            last_letter = rec.serial_no[-1]
            new_sl_no = rec.serial_no[:-1] + letter_dict.get(last_letter)


            new_fd_record.write({
                    'serial_no': new_sl_no,  
                    'acc_number': rec.acc_number,
                    'start_date': rec.maturity_date,
                    'maturity_date': self.mr_dt,
                    'principal_amt': rec.recovered_or_renewed_amt,
                    'rate_of_interest': rec.rate_of_interest,
                    'maturity_amt': 0,
                    'fd_type': rec.fd_type,
                    'is_fd_live': True, 
                    'recovered_or_renewed_dt': None,
                    'recovered_or_renewed_amt': 0,
                    'maturity_interest_net': 0,
                    'tds': 0,
                    'maturity_interest_gross': 0,
                })