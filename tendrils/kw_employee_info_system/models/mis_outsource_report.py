from odoo import fields, models, api, tools
import datetime
from datetime import date


class ContractEndReport(models.Model):
    _name = 'mis_outsources_report'
    _description = 'Outsource  Report'

    def get_fiscal_year(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.datetime.today().date()),
             ('date_stop', '>=', datetime.datetime.today().date())])

        return current_fiscal

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    fiscalyear_id = fields.Many2one('account.fiscalyear', string='FY', default=get_fiscal_year, required=True)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)
    resource_type = fields.Char(string="Resource Type", required=True)
    head_count = fields.Integer(string="Headcount", required=True) 
    
    @api.model
    def create(self,vals):
        records= self.env['mis_resources_report'].search([('fiscalyear_id', '=', vals.get('fiscalyear_id')), ('month', '=', vals.get('month'))])
        if records:
            count_of=records.head_count + vals.get('head_count')
            records.write({
            'resource_type':'Outsource CSM',
            'head_count': count_of
            })
            
        else:
            self.env['mis_resources_report'].create({
                        'fiscalyear_id' : vals.get('fiscalyear_id'),
                        'month' : vals.get('month'),
                        'resource_type':'Outsource CSM',
                        'head_count': vals.get('head_count')
                    })             
               
        return super(ContractEndReport,self).create(vals)  
            
    
    
    def write(self,vals):
        count_of = 0
        records= self.env['mis_resources_report'].search([('fiscalyear_id', '=', self.fiscalyear_id.id), ('month', '=',self.month)])
        # print("records===================",self.fiscalyear_id.id,self.month,self.head_count,records.head_count)
        records2= self.search([('fiscalyear_id', '=', self.fiscalyear_id.id), ('month', '=',self.month),('id', '!=', self.id)])
        # print("record2vvvvvvvvvvvvv", records2)
        for rec in records2:
            count_of += rec.head_count
        count_of += vals.get('head_count')
        records.write({
            'resource_type':'Outsource CSM',
            'head_count': count_of
        }) 
               
       
        return  super(ContractEndReport,self).write(vals)          
        
        
