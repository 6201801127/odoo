from odoo import api, fields, models


class KwResBranch(models.Model):
    _name = 'kw_res_branch'
    _description = "Branch"
    _rec_name = 'alias'
    _order = 'city asc'

    branch_code = fields.Char('Branch Code/Ref.')
    code = fields.Char('Code')
    kw_id = fields.Integer('Tendrils ID')
    name = fields.Char('Name', required=True)
    address = fields.Text('Branch Address', size=252)
    telephone_no = fields.Char('Telephone No.')
    gst_no = fields.Char('GSTIN')
    state_id = fields.Many2one('res.country.state', 'State')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, readonly=True)
    email = fields.Char('Email')
    website = fields.Char('Website')
    country = fields.Many2one('res.country', 'Country')
    fax = fields.Char('Fax')
    city = fields.Char('City')
    zipcode = fields.Char('Zipcode')
    active = fields.Boolean('Active', default=True)
    location = fields.Many2one('kw_location_master', string="Location")
    alias = fields.Char(string="Alias")
    branch_unit_ids = fields.One2many(comodel_name='kw_res_branch_unit', inverse_name='branch_id', string='Unit Name')
    inventory_ref = fields.Char('Inventory Ref')
    recruitment_ref = fields.Char('Recruitment Ref')
    guest_d = fields.Boolean("Guest", compute='fetch_guest', default=False)

    def fetch_guest(self):
        for rec in self:
            guest = self.env['kw_branch_guest_house'].search([('branch_code', '=', rec.id)])
            if guest:
                rec.guest_d = True

    @api.onchange('country')
    def fetch_states(self):
        if self.country:
            self.state_id = False
            return {'domain': {'state_id': ([('country_id', '=', self.country.id)])}}

    @api.multi
    def btn_view_details(self):
        view_id = self.env.ref('kw_branch_master.kw_res_branch_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_res_branch',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.id,
        }
        return action

    @api.multi
    def btn_view_guest_details(self):
        branch_data = self.env['kw_branch_guest_house'].search([('branch_code', '=', self.id)])
        # print("=======================>", branch_data)
        view_id = self.env.ref('kw_branch_master.kw_res_guest_house_form').id
        tree_view_id = self.env.ref('kw_branch_master.kw_res_guest_house_tree').id
        if len(branch_data) > 1:
            action = {
                'name': 'Guest House',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_branch_guest_house',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': tree_view_id,
                'target': 'self',
                'views': [(tree_view_id, 'tree')],
                'domain': [('id', 'in', branch_data.ids)]
            }

        else:
            action = {
                'name': 'Guest House',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_branch_guest_house',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'res_id': branch_data.id,
            }
        return action

    # def _get_name(self):
    #     """ Utility method to allow name_get to be overridden without re-browse the partner """
    #
    #     partner = self
    #     name = partner.city or ''
    #     if self._context.get('city'):
    #         name = partner.city
    #     return name

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         record_name = str(record.name)
    #         if record.city:
    #             record_name = record_name+", "+record.city
    #         result.append((record.id, record_name))
    #     return result
