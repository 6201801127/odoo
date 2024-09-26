# added by gouranga on 27-Dec-2021 to maintain the file lifecycle master
from odoo import models,fields,api

class FileStage(models.Model):

    _name = 'smart_office.file.stage'
    _description = 'Stores lifecycles of files.'
    _order = 'id asc'

    name = fields.Char("Stage Name",required=True)
    code = fields.Char("Code",required=True)
    use_on_report = fields.Boolean("Use on Reporting")
    description = fields.Text("Description")

    _sql_constraints = [('code_uniq', 'UNIQUE (code)',  'Code must be unique!')]

    @api.model
    def create(self,vals):
        res = super(FileStage,self).create(vals)
        self.env.user.notify_success("Tracking Stage Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(FileStage, self).write(vals)
        self.env.user.notify_success("Tracking Stage Saved Successfully.")
        return res
    
class CorresspondenceStage(models.Model):

    _name = 'smart_office.correspondence.stage'
    _description = 'Stores lifecycles of correspondences.'
    _order = 'id asc'

    name = fields.Char("Stage Name",required=True)
    code = fields.Char("Code",required=True)
    description = fields.Text("Description")

    _sql_constraints = [('code_uniq', 'UNIQUE (code)',  'Code must be unique!')]

    @api.model
    def create(self,vals):
        res = super(CorresspondenceStage,self).create(vals)
        self.env.user.notify_success("Tracking Stage Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(CorresspondenceStage, self).write(vals)
        self.env.user.notify_success("Tracking Stage Saved Successfully.")
        return res


class CorresspondenceUserwiseStage(models.Model):

    _name = 'correspondence.userwise.stage'
    _description = 'Stores lifecycles of userwise correspondences.'
    _order = 'id asc'

    name = fields.Char("Stage Name",required=True)
    code = fields.Char("Code",required=True)
    description = fields.Text("Description")

    _sql_constraints = [('code_uniq', 'UNIQUE (code)',  'Code must be unique!')]

    @api.model
    def create(self,vals):
        res = super(CorresspondenceUserwiseStage,self).create(vals)
        self.env.user.notify_success("Userwise Tracking Stage Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(CorresspondenceUserwiseStage, self).write(vals)
        self.env.user.notify_success("Userwise Tracking Stage Saved Successfully.")
        return res

class DispatchLetterStages(models.Model):
    _name = 'dispatch.letter.stage'
    _description = "Dispatch Letter Stages"
    
    name = fields.Char("Stage Name",required=True)
    code = fields.Char("Code",required=True)
    description = fields.Text("Description")
    use_on_report = fields.Boolean("Use on Reporting")
    
    _sql_constraints = [('code_uniq', 'UNIQUE (code)',  'Code must be unique!')]
    
    @api.model
    def create(self,vals):
        res = super(DispatchLetterStages,self).create(vals)
        self.env.user.notify_success("Userwise Tracking Stage Created Successfully.")
        return res

    @api.multi
    def write(self, vals):
        res = super(DispatchLetterStages, self).write(vals)
        self.env.user.notify_success("Userwise Tracking Stage Saved Successfully.")
        return res