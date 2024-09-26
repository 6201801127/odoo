from odoo import models, fields, api

class kw_grievance_master(models.Model):
    _name        = 'kw.grievance.type'
    _description = 'A model to manage grievance categories'
    _rec_name    = 'name'


    def get_spoc(self):
        spoc_lst=[]
        spoc = self.env['kw_grievance_spoc_master'].sudo().search([])
        for record in spoc:
            # print('record',spoc)
            for rec in record.spoc_person_id:
                # print('rec',record.spoc_person_id)
                spoc_lst.append(rec.id)
        # print('rec',spoc_lst)   
        return spoc_lst

    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    # department_id = fields.Many2one('hr.department',string="Concerned Section",domain="[('dept_type.code','=','section')]")
    concerned_person_ids = fields.Many2many(string="Concerned Person",comodel_name='hr.employee',default=get_spoc)