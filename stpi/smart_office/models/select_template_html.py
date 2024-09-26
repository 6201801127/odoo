
from odoo import models,fields,api
from odoo.exceptions import ValidationError

class SelectTemplate(models.Model):
    _name = 'select.template.html'
    _description = 'Select Template'

    name = fields.Char('Name',required=True)
    template = fields.Html('Template',required=True)

    @api.constrains('name')
    def validate_name(self):
        for template in self:
            duplicate_template = self.search([('name','=ilike',template.name)]) - self
            if duplicate_template:
                raise ValidationError("Name must be unique")

    # @api.constrains('template')
    # def validate_template(self):
    #     for template in self:
    #         duplicate_template = self.search([('template','=ilike',template.template)]) - self
    #         if duplicate_template:
    #             raise ValidationError("Template must be unique")
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = f"{self.name}-Copy"
        return super(SelectTemplate, self).copy(default=default)

    @api.model
    def create(self,vals):
        res = super(SelectTemplate,self).create(vals)
        self.env.user.notify_success("Template Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(SelectTemplate, self).write(vals)
        self.env.user.notify_success("Template Saved Successfully.")
        return res