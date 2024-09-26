from odoo import models, fields, api, tools


class CourtCaseType(models.Model):
    _name               = 'court.case.type'
    _description        = 'Court Case Type'
    _rec_name           = 'case_type'
    

    case_type           = fields.Char(string="Case Type / मामले का प्रकार")
    code                = fields.Char(string='Case Type Code / केस टाइप कोड')
   

class CourtCaseSubType(models.Model):
    _name               = 'court.case.sub.type'
    _description        = 'Court Case Subtype'
    _rec_name           = 'case_sub_type'
    
    case_sub_type       = fields.Char(string = "Case Sub-type / केस उप-प्रकार")
    case_types_id         = fields.Many2one('court.case.type',string="Case types Code / केस प्रकार कोड")
    
class CourtLocation(models.Model):
    _name = 'court.location'
    _description = 'Court location master model'

    name = fields.Char(string='Location / स्थान')