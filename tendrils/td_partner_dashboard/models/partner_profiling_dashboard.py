# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import Counter
import datetime
from collections import defaultdict


class PartnerProfilingDashboard(models.Model):
    _name = 'partner_profiling_dashboard'
    _description = "Partner Profiling Dashboard"


    @api.model
    def get_profiling_data(self):
        partner_type_ids = self.env['kw_partner_type_master'].search([])
        partner_type_list,partner_count_list = [],[]
        for rec in partner_type_ids:
            partner_data_count = self.env['res.partner'].search_count([('partner_type_id','=',rec.id),('is_partner','=',True)])
            partner_type_list += [str(rec.name)]
            partner_count_list += [partner_data_count]
        
        return [partner_type_list,partner_count_list]

    @api.model
    def get_industries_data(self):
        industry_ids = self.env['res.partner.industry'].search([])
        partner_count_list = []
        for rec in industry_ids:
            partner_data_count = self.env['res.partner'].search_count([('industy_domain_ids','in',[rec.id]),('is_partner','=',True)])
            partner_count_list += [[str(rec.name),partner_data_count]]
        return [partner_count_list]


    @api.model
    def get_technology_data(self):
        technology_ids = self.env['kw_partner_tech_service_master'].search([('type','=','2')])
        partner_count_list = []
        for rec in technology_ids:
            partner_data_count = self.env['res.partner'].search_count([('tech_ids','in',[rec.id]),('is_partner','=',True)])
            partner_count_list += [[str(rec.name),partner_data_count]]
        return [partner_count_list]


    @api.model
    def get_service_data(self):
        partner_data = self.env['res.partner'].sudo().search([('is_partner','=',True)])

        service_counter = Counter()
        
        for partner in partner_data:
            if partner.service_offering_ids:
                for service in partner.service_offering_ids:
                    if service.type == '1': 
                        service_counter[service.name] += 1

        service_dict = {str(k): v for k, v in service_counter.items()}

        return service_dict


    @api.model
    def get_geographic_data(self):
        partner_data = self.env['res.partner'].sudo().search([('is_partner','=',True)])
        partner_geographic_data = defaultdict(lambda: defaultdict(Counter))
        
        for partner in partner_data:
            if partner.yoi:
                year = datetime.datetime.strptime(str(partner.yoi), '%Y-%m-%d').year
                
                if partner.geography_of_business:
                    for geography in partner.geography_of_business:
                        if geography.code == 'IN':
                            partner_geographic_data[year]['India'][geography.name] += 1
                        else:
                            partner_geographic_data[year]['Other'][geography.name] += 1

        geographic_data = {
            year: {
                'India': {str(k): v for k, v in partner_geographic_data[year]['India'].items()},
                'Other': {str(k): v for k, v in partner_geographic_data[year]['Other'].items()}
            }
            for year in partner_geographic_data
        }

        return geographic_data


