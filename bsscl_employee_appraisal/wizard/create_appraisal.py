from odoo import models, fields, _ ,api
from datetime import date
from odoo.exceptions import ValidationError

class BssclAppraisalCreateWizard(models.TransientModel):

    _name = "create.appraisal.wizard"
    _description = "Wizard model for Create Appraisal"

    # @api.model
    # def default_get(self, field_list):
    #     result = super(BssclAppraisalCreateWizard, self).default_get(field_list)
    #     todays_date = date.today()
    #     char_yr = str(todays_date.year)
    #     emp_contract = self.env['account.fiscalyear'].search(
    #                 [('name', '=', char_yr)],limit=1)
    #     result['abap_period'] = emp_contract.id
    #     return result

    employee_ids = fields.Many2many(comodel_name='hr.employee',relation="create_appraisal_wiz_hr_employee_rel", column1='create_appraisal_wiz',column2='hr_emp', string='Employees / कर्मचारी',tracking=True)
    abap_period = fields.Many2one(comodel_name='account.fiscalyear', string='APAR Period / एपीएआर अवधि')

    
    """ ******* Validation work when manager try to create appraisal for none contract user/Contract not in running state for user/ Duplicate appraisal for same fiscal year *********
    """
    @api.constrains('employee_ids','abap_period')
    @api.onchange('employee_ids','abap_period')
    def _onchange_emp_abap(self):
        model_id = self.env['bsscl.employee.appraisal'].sudo().search([])
        for rec in model_id:
            emp_id = self.employee_ids.ids
            for record in emp_id:
                if rec.employee_id.id == record and rec.apar_period_id.id == self.abap_period.id:
                    raise ValidationError("You can not create duplicate appraisal for %s in fiscal year %s / आप वित्तीय वर्ष %s में %s के लिए डुप्लीकेट मूल्यांकन नहीं बना सकते" % (rec.employee_id.first_name,rec.apar_period_id.name,rec.apar_period_id.name,rec.employee_id.first_name))
        
        hr_contract = self.env['hr.contract'].sudo().search([])
        running_hr_contract = self.env['hr.contract'].sudo().search([('state','=','open')])

        if hr_contract:
            if running_hr_contract:
                emp_id = self.employee_ids.ids
                if emp_id:
                    for rec in emp_id:
                        query = """ select name from hr_employee 
                                    where id = %(record)s
                                """
                        query_params = {'record':rec}
                        self.env.cr.execute(query,query_params)
                        data = self.env.cr.fetchall()
                        for emp_name in data:
                            for emp in emp_name:
                                employee_name = emp
                                print('emp========================',emp)
                        print("Query==================================",query)
                        print("rec_name+++++++++++++++++++++++++++++++++++++++",data)
                        if (rec in hr_contract.employee_id.ids) and (rec not in running_hr_contract.employee_id.ids):
                            raise ValidationError('Contract not in running state for %s / %s के लिए अनुबंध चालू स्थिति में नहीं है' % (employee_name,employee_name))
                        if (rec not in hr_contract.employee_id.ids) and (rec not in running_hr_contract.employee_id.ids):
                            raise ValidationError('User %s is not in contract. so, you can not create appraisal for %s / उपयोक्ता %s अनुबंध में नहीं है। इसलिए, आप %s के लिए मूल्यांकन नहीं बना सकते' % (employee_name,employee_name,employee_name,employee_name))
            if not  running_hr_contract:
                raise ValidationError('No any contract found in running State')
        else:
            raise ValidationError('Contract not found please create contract first')
            
    def create_appraisal_action_button(self):
        for rec in self:
            for employee in rec.employee_ids:
                emp_contract = self.env['hr.contract'].search(
                    [('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
                self.env['bsscl.employee.appraisal'].create({
                    'state': 'draft',
                    'employee_id': employee.id,
                    'apar_period_id': rec.abap_period.id,
                    'branch_id': employee.user_id.default_branch_id.id,
                    'template_id': emp_contract.job_id.template_id.id,
                })
               
                
            
