from odoo import fields,models,api

class Training(models.Model):
    _name           =   "training"
    _description    =   "Training Plan"

    category        =   fields.Many2one('category',string='Category')
    name            =   fields.Char(string='Training Name',required=True)
    training_date   =   fields.Date(string='Training Date',default=fields.Date.context_today,required=True)
    total_hour      =   fields.Char(string='Total Hour',required=True)
    projects        =   fields.Many2many('project.project',string='Training On Projects')
    sessions_ids    =   fields.One2many('session','training_id',string='Session')
    description     =   fields.Text(string='Description',help="Description of training.")

class Category(models.Model):
    _name           =   'category'
    _description    =   'Category Details'
    _rec_name       =   'category_name'

    category_name   =   fields.Char(string='Catagory Name',required=True)
    active          =   fields.Boolean(default=True)

class Session(models.Model):
    _name           =   'session'
    _description    =   'Session Details'

    name            =   fields.Char(string='Session Name',required=True)
    training_id     =   fields.Many2one('training',string='Training Name')
    trainer_name    =   fields.Many2one('res.partner',string='Trainer Name',required=True,ondelete='restrict')
