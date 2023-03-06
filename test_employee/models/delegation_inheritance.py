from odoo import api, fields, models

class Screen(models.Model):
    _name = "delegation.screen"
    _description = "Screen"

    size = fields.Float(string="screen size in inches")

class Keyboard(models.Model):
    _name = "delegation.keyboard"
    _description = "Keyboard"

    layout = fields.Char(string="Layout")

class Laptop(models.Model):
    _name = "delegation.laptop"
    _description = "Laptop"

    _inherits ={
        'delegation.screen':'screen_id',
        'delegation.keyboard':'keyboard_id',    
    }
    name = fields.Char("Name")
    maker = fields.Char("Maker")
    #a laptop has a screen
    screen_id = fields.Many2one('delegation.screen', required=True, ondelete="cascade")
    #a laptop has a keyboard
    keyboard_id = fields.Many2one('delegation.keyboard', required=True, ondelete="cascade")

    def get_values(self):
        for case in self:
            print("values", case.name, case.maker, case.size, case.layout)
