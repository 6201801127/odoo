from odoo import api,fields, models,_

class VendorwiseWizard(models.TransientModel):

    _name = 'vendor.wizard'
    _description = 'vendorwise wizard'

    financial_year_id = fields.Many2one('account.fiscalyear', 'Fiscal Year')


    @api.multi
    def wizard_fiscal_year(self):
        vendor_list = [] 
        partner_name = []
        name = str('Vendor wise Records')+ '('+str(self.financial_year_id.name)+')'
        employee = self.env['hr.employee'].search([('vendor_id', '!=', False)])
        vendors_summary = self.env['hr.mis.vendorwise.records']
        vendor_details = vendors_summary.search([])
        for partner in employee:
            partner_name.append(partner.id)
        # print('partner_name', partner_name)
        for rec_ven in vendor_details:
            vendor_list.append(rec_ven.vendor_id.id)
        # print('vendor_list', vendor_list)
        for rec in partner_name:
            # print('records',rec, vendor_list)
            if rec not in vendor_list:
                vendors_summary.create({'vendor_id': rec,
                    'financial_year_id': self.financial_year_id.id})
        
        return{
            'type' : 'ir.actions.act_window',
            'name' : name,
            'res_model' : 'hr.mis.vendorwise.records',
            'domain' : [('financial_year_id','=',self.financial_year_id.id)],            
            'view_mode' : 'tree',
            'target' : 'main',
            'context': {'default_financial_year_id': self.financial_year_id.id}
        }