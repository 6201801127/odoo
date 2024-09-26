from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    ir_attachment_ids = fields.One2many('ir.attachment', 'project_id', string='Document Type',
                                        track_visibility='always')

    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        contract_obj = self.env['partner.contract']
        change_request_obj = self.env['change.request']
        budget_obj = self.env['crossovered.budget']
        quality_obj = self.env['qc.inspection']
        acceptance_obj = self.env['acceptance.inspection']
        contract_ids, change_ids, budget_ids, quality_ids, acceptance_ids = [], [], [], [], []
        # Contract
        contract_attachment = contract_obj.search([('related_project', '=', self.id)])
        if contract_attachment:
            for lines in contract_attachment:
                contract_ids.append(lines.id)
        # Change Request
        change_attachment = change_request_obj.search([('project_id', '=', self.id)])
        if change_attachment:
            for lines in change_attachment:
                change_ids.append(lines.id)
        # Budget
        budget_attachment = budget_obj.search([('analytic_account_id', '=', self.analytic_account_id.id)])
        if budget_attachment:
            for lines in budget_attachment:
                budget_ids.append(lines.id)
        # Quality
        quality_attachment = quality_obj.search([('project_id', '=', self.id)])
        if quality_attachment:
            for lines in quality_attachment:
                quality_ids.append(lines.id)
        # Acceptance
        acceptance_attachment = acceptance_obj.search([('project_id', '=', self.id)])
        if acceptance_attachment:
            for lines in acceptance_attachment:
                acceptance_ids.append(lines.id)
        action['domain'] = str([
            '|', '|', '|', '|', '|', '|',
            '&',
            ('res_model', '=', 'project.project'),
            ('res_id', 'in', self.ids),
            '&',
            ('res_model', '=', 'project.task'),
            ('res_id', 'in', self.task_ids.ids),
            '&',
            ('res_model', '=', 'partner.contract'),
            ('res_id', 'in', (contract_ids)),
            '&',
            ('res_model', '=', 'change.request'),
            ('res_id', 'in', (change_ids)),
            '&',
            ('res_model', '=', 'crossovered.budget'),
            ('res_id', 'in', (budget_ids)),
            '&',
            ('res_model', '=', 'qc.inspection'),
            ('res_id', 'in', (quality_ids)),
            '&',
            ('res_model', '=', 'acceptance.inspection'),
            ('res_id', 'in', (acceptance_ids)),
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            contract_obj = self.env['partner.contract']
            change_request_obj = self.env['change.request']
            budget_obj = self.env['crossovered.budget']
            quality_obj = self.env['qc.inspection']
            acceptance_obj = self.env['acceptance.inspection']
            contract_ids, change_ids, budget_ids, quality_ids, acceptance_ids = [], [], [], [], []
            # Contract
            contract_attachment = contract_obj.search([('related_project', '=', project.id)])
            if contract_attachment:
                for lines in contract_attachment:
                    contract_ids.append(lines.id)
            # Change Request
            change_attachment = change_request_obj.search([('project_id', '=', project.id)])
            if change_attachment:
                for lines in change_attachment:
                    change_ids.append(lines.id)
            # Budget
            budget_attachment = budget_obj.search([('analytic_account_id', '=', project.analytic_account_id.id)])
            if budget_attachment:
                for lines in budget_attachment:
                    budget_ids.append(lines.id)
            # Quality
            quality_attachment = quality_obj.search([('project_id', '=', project.id)])
            if quality_attachment:
                for lines in quality_attachment:
                    quality_ids.append(lines.id)
            # Acceptance
            acceptance_attachment = acceptance_obj.search([('project_id', '=', project.id)])
            if acceptance_attachment:
                for lines in acceptance_attachment:
                    acceptance_ids.append(lines.id)
            project.doc_count = Attachment.search_count([
                '|', '|', '|', '|', '|', '|',
                '&',
                ('res_model', '=', 'project.project'),
                ('res_id', 'in', self.ids),
                '&',
                ('res_model', '=', 'project.task'),
                ('res_id', 'in', self.task_ids.ids),
                '&',
                ('res_model', '=', 'partner.contract'),
                ('res_id', 'in', (contract_ids)),
                '&',
                ('res_model', '=', 'change.request'),
                ('res_id', 'in', (change_ids)),
                '&',
                ('res_model', '=', 'crossovered.budget'),
                ('res_id', 'in', (budget_ids)),
                '&',
                ('res_model', '=', 'qc.inspection'),
                ('res_id', 'in', (quality_ids)),
                '&',
                ('res_model', '=', 'acceptance.inspection'),
                ('res_id', 'in', (acceptance_ids)),
            ])

    @api.model
    def create(self, vals):
        rec = super(Project, self).create(vals)
        if rec.ir_attachment_ids:
            for lines in rec.ir_attachment_ids:
                lines.update({'res_model': 'project.project', 'res_id': rec.id})
        return rec
