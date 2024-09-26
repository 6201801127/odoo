import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TourGuesthouseMaster(models.Model):
    _name = 'kw_tour_guest_house'
    _description = "Tour Guest House"

    country_id = fields.Many2one("res.country", "Country Name", required=True)
    city_id = fields.Many2one("kw_tour_city", "City Name", required=True)
    name = fields.Char('Guest House Name', required=True)
    address = fields.Text("Address")
    contact_person_id = fields.Many2many(string='Contact Person', comodel_name='res.partner',
                                         domain=[('company_type', '=', 'individual')])
    spoc_person_id = fields.Many2one("res.partner", "SPOC Person", required=True)
    active = fields.Boolean(default=True)

    @api.constrains('name', 'city_id', 'country_id')
    def validate_guest_house(self):
        regex = re.compile(r"[@_!#$%^&*()|<>?/\}{~:]")
        for guest_house in self:
            if regex.search(guest_house.name) != None:
                raise ValidationError("Special characters are not allowed in guest house.")

            record = self.env['kw_tour_guest_house'].search([]) - guest_house
            for info in record:
                if info.name.lower() == guest_house.name.lower() and info.city_id == guest_house.city_id \
                        and info.country_id == guest_house.country_id:
                    raise ValidationError(f"Guest House {guest_house.name} already exists.")
