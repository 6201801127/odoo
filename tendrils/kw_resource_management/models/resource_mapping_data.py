from odoo import models, fields, api
import requests, json
import datetime
from datetime import date
from datetime import datetime as dt


class ResourceMappingData(models.Model):
    _name = "kw_resource_mapping_data"
    _description = "Resource Mapping Data"

    sl_no = fields.Integer('Sl No',compute = 'compute_sl_no')
    action_status = fields.Char('ActionStatus')
    desg_type = fields.Char('Mode Offsite/Onsite')
    desgtype = fields.Char('DESGTYPE')
    experience = fields.Float(string='Experience')
    min_experience = fields.Float(string='Min Experience')
    month_bill = fields.Char(string='Month Bill')
    from_date = fields.Date('Engagement Start Date ')
    to_date = fields.Date('Engagement End Date ')
    engagement_type = fields.Char('Engagement Type')
    resource_no = fields.Integer(string='No Resource Required')
    resource_available = fields.Integer(string='No Resource Available')
    qualification_id = fields.Char(string='Qualification ID')
    resource_id = fields.Integer(string='Resource ID')
    no_of_month = fields.Float(string='No Of Month')
    module_short_name = fields.Char(string='Opportunity Name')
    opportunity_id = fields.Many2one('crm.lead',string = 'Opportunity')
    project_type_name = fields.Char(string='Project Type Name')
    tagged_res = fields.Char(string='No of resources New Requirement form R&CM')
    designation = fields.Char(string='Position')
    fiscal_yr = fields.Char(string='FY Year Name')
    prof_qualification = fields.Char(string='Prof Qualification')
    qualification = fields.Char(string='Qualification')
    work_location = fields.Char(string='Location')
    acc_holder = fields.Char(string='Account Holder')
    technology_id = fields.Char(string='Technology ID')
    user_name = fields.Char(string='User Name')
    technology = fields.Char(string='Technology')
    proejct_manager_name = fields.Char(string='Project Manager')
    proejct_manager_id = fields.Many2one('hr.employee',string='Project Manager')
    sbu_name = fields.Char(string='SBU Name')
    kw_sbu_id = fields.Integer(string='SBU ID')
    kw_sbu_head_id = fields.Many2one('hr.employee',string='SBU')
    check_representative = fields.Boolean(string='Representative', compute='_representative_check')
    active = fields.Boolean(string="Active", default=True)
    resource_required = fields.Integer(string='No of resources Requirement form R&CM', compute="compute_resource_required")
    account_holder_id = fields.Many2one('hr.employee',string='Acc Holder')
    csg_id = fields.Many2one('hr.employee', string='CSG')
    opp_code = fields.Char(string = 'OPP Code')
    client = fields.Char(string = 'Client')
    reviewer_id = fields.Many2one('hr.employee',string = 'Reviewer')
    wo_plan_date = fields.Date(string = 'WO Plan Date')
    bid_status = fields.Selection(string='Bid Status',selection=[('1', 'Won'), ('5', 'Result Awaited'),('10', 'Shortlisted'),('14', 'Submitted')])
    bid_status_name = fields.Char(string="BidStatus")
    bid_status_id = fields.Integer(string="Bidstatus Id")
    opportunity_status = fields.Integer(string="Opportunity")

    @api.depends('resource_no', 'resource_available')
    def compute_resource_required(self):
        for rec in self:
            if rec.resource_no and rec.resource_available:
                rec.resource_required = rec.resource_no - rec.resource_available

    def compute_sl_no(self):
            records = self.search([], order="id asc")
            cnt = 1 
            for rec in records:
                rec.sl_no = cnt
                cnt += 1  
            

    @api.multi
    def sync_resource_mapping_data(self, *args):
        project_url = self.env.ref('kw_resource_management.kw_resource_mapping_parameter').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = json.dumps({})
        resp_result = requests.post(project_url, headers=header, data=data)
        resp = json.loads(resp_result.text)
        response_resource_ids = [rec['INT_RESOURCE_ID'] for rec in resp]
        if response_resource_ids:
            query = """
                UPDATE kw_resource_mapping_data
                SET active = FALSE
                WHERE resource_id NOT IN %s
            """
            self.env.cr.execute(query, (tuple(response_resource_ids),))

        records_to_update = []
        records_to_create = []
        for rec in resp:
            resource_id = rec['INT_RESOURCE_ID']
            existing_record_query = """
                SELECT id FROM kw_resource_mapping_data
                WHERE resource_id = %s
                LIMIT 1
            """
            self.env.cr.execute(existing_record_query, (resource_id,))
            existing_record = self.env.cr.fetchone()

            resource_data = {
                'action_status': rec['ActionStatus'],
                'desg_type': rec['CHAR_DESG_TYPE'],
                'desgtype': rec['CHR_DESGTYPE'],
                'experience': rec['DEC_EXPERIENCE'],
                'min_experience': rec['DEC_MINEXPERIENCE'],
                'month_bill': rec['DEC_MONTH_BILL'],
                'from_date': rec['DTM_FROM_DATE'] if rec['DTM_FROM_DATE'] else False,
                'to_date': rec['DTM_TO_DATE'] if rec['DTM_TO_DATE'] else False,
                'engagement_type': rec['ENGAGEMENTTYPE'],
                'resource_no': rec['INT_NO_RESOURCE'],
                'qualification_id': rec['INT_QUALIFICATION_ID'],
                'no_of_month': rec['NOOFMONTH'],
                'module_short_name': rec['NVCH_MODULESHORTNAME'],
                'project_type_name': rec['ProjectTypeName'],
                'tagged_res': rec['TAGGED_RES'],
                'designation': rec['VCH_DESIGNATION'],
                'fiscal_yr': rec['VCH_FY_NAME'],
                'prof_qualification': rec['VCH_PROF_QUALIFICATION'],
                'qualification': rec['VCH_QUALIFICATION'],
                'work_location': rec['VCH_WORK_LOC'],
                'technology_id': rec['intTechnology'],
                'user_name': rec['username'],
                'technology': rec['vchTechnology'],
                'proejct_manager_name': rec['PM'],
                'proejct_manager_id': self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['PMId']))], limit=1).id if rec['PMId'] else False,
                'sbu_name': rec['SBU'],
                'kw_sbu_id': rec['intSBUId'],
                'kw_sbu_head_id': self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['SBUHeadId']))], limit=1).id if rec['SBUHeadId'] else False,
                'account_holder_id': self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['acholderid']))], limit=1).id if rec['acholderid'] else False,
                'csg_id': self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['CSGmemberId']))], limit=1).id if rec['CSGmemberId'] else False,
                'opp_code': rec['oppCode'],
                'client': rec['Client'],
                'reviewer_id': self.env['hr.employee'].sudo().search([('kw_id', '=', int(rec['ProjectReviewerId']))], limit=1).id if rec['ProjectReviewerId'] else False,
                'wo_plan_date': rec['WOPlanDate'] if rec['WOPlanDate'] else False,
                'active': True,
                'bid_status_name': rec['BDStatus'],
                'bid_status_id': int(rec['BDStatusId']),
                'opportunity_id': self.env['crm.lead'].sudo().search([('kw_opportunity_id', '=', int(rec['oppId']))], limit=1).id if rec['oppId'] else False,
            }

            if existing_record:
                records_to_update.append((resource_data, existing_record[0]))
            else:
                resource_data['resource_id'] = resource_id
                records_to_create.append(resource_data)

        # Batch update existing records
        for data, record_id in records_to_update:
            self.env['kw_resource_mapping_data'].sudo().browse(record_id).write(data)

        # Batch create new records
        self.env['kw_resource_mapping_data'].sudo().create(records_to_create)


    @api.model
    def get_resource_mapping_data(self):
        tree_view_id = self.env.ref('kw_resource_management.kw_resource_mapping_data_tree').id
        search_view_id = self.env.ref('kw_resource_management.kw_resource_mapping_data_search').id
        eq_approve_data = self.env['kw_eq_estimation'].search([('state', '=', 'grant')])
        kw_op_id = eq_approve_data.mapped('kw_oppertuinity_id')

        domain = [('opportunity_id', 'in', kw_op_id.ids),('bid_status_id', 'in', [1, 5, 10, 14])]
      

        action = {
            'name': 'Resource Mapping',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'kw_resource_mapping_data',
            'views': [(tree_view_id, 'tree'), (search_view_id, 'search')],
            'domain': domain,
        }

        return action

    @api.model
    def get_resource_mapping_data_view(self):
        tree_view_id = self.env.ref('kw_resource_management.kw_resource_mapping_data_tree').id
        search_view_id = self.env.ref('kw_resource_management.kw_resource_mapping_data_search').id

        # m_data = self.env['kw_resource_mapping_data'].search([])
        # resource_opp_data = m_data.mapped('opportunity_id')
        # print(resource_opp_data, "=========resource_opp_data==========")

        eq_approve_data = self.env['kw_eq_estimation'].search([('state', '=', 'grant')])
        kw_op_id = eq_approve_data.mapped('kw_oppertuinity_id')

        domain = [('opportunity_id', 'in', kw_op_id.ids),('bid_status_id', 'in', [1, 5, 10, 14])]
      

        action = {
            'name': 'Resource Mapping',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'kw_resource_mapping_data',
            'views': [(tree_view_id, 'tree'), (search_view_id, 'search')],
            'domain': domain,
        }

        return action

    @api.multi
    def update_quantity(self):
        tree_view_id = self.env.ref('kw_resource_management.resource_qty_update_wizard_form').id
        domain = []
        # if self.env.user.has_group('kw_resource_management.group_sbu_representative'):
        #     domain = [('kw_sbu_head_id', '=', self.env.user.employee_ids.sbu_master_id.kw_id)]
        # if self.emp_category:
        #     domain += [('emp_category', '=', self.emp_category.id), ]
        # if self.employement_type:
        #     domain += [('employement_type', '=', self.employement_type.id), ]

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Update Resource available Quantity',
            'views': [(tree_view_id, 'form')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'resource_qty_update_wizard',
            'target': 'new',
            'context': {'default_resource_map_id': self.id, 'default_resource_no': self.resource_no,
                        'default_module_short_name': self.module_short_name},
            'domain': domain
        }
        # print(action,"action----------->>>>>>>>>")
        return action

    def _representative_check(self):
        for rec in self:
            if self.env.user.has_group('kw_resource_management.group_sbu_representative'):
                sbu_kw_id = self.env.user.employee_ids.kw_id
                # print("sbu_kw_id >>>>>>>>>>> ", sbu_kw_id, rec.kw_sbu_head_id)
                if sbu_kw_id == rec.kw_sbu_head_id.id:
                    rec.check_representative = True
                else:
                    rec.check_representative = False
            else:
                rec.check_representative = False

