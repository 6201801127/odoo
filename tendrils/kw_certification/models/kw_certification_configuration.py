from odoo.exceptions import ValidationError
from odoo import models, fields, api


    # Certification Master Configuration

class KwCertificationMaster(models.Model):
    _name = 'certification_master'
    _description = ""
    _rec_name = 'name'
    
    
    name = fields.Char(string="Name",required= True)
    oem = fields.Char("OEM")
    active = fields.Boolean(string="Active", default=True)
    certification_fees = fields.Float(string="Fees")
    code=fields.Char(string="Code")
    
    @api.constrains('name', )
    def get_no_duplicate_record(self):
        record = self.env['certification_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError('This name alredy Exist for this certification') 
    
     
class KwCertificationTechnology(models.Model):
    _name = 'kw_certification_technology_master'
    _description = ""
    _rec_name = 'name'
    
    
    name = fields.Char(string="Name", required= True)
    active = fields.Boolean(string="Active",default=True) 
    code=fields.Char(string="Code")


    @api.constrains('name', )
    def get_no_duplicate_record(self):
        record = self.env['kw_certification_technology_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
               raise ValidationError('This name alredy Exist for this technology')  
      


     # Certification Budget Configuration
 
class KwCertificationBudget(models.Model):
    _name = 'kw_certification_budget_master'
    _description = ""
    _rec_name = 'certificate_id'
    
       
    certificate_id = fields.Many2one("kwmaster_stream_name",string="Certification",domain="[('course_id.code', '=', 'cert')]", required=True)
    budget=fields.Float(string="Budget", required=True)
    active=fields.Boolean(string="Active", default=True)  
    
    @api.constrains('certificate_id')
    def get_no_duplicate_record(self):
        for rec in self:
            certification_name = self.env['kw_certification_budget_master'].search([('certificate_id', '=', rec.certificate_id.id),
                                           ('id', '!=', rec.id)])
            if certification_name:
                raise ValidationError('This certification budget alredy Exist ')   
    
      
