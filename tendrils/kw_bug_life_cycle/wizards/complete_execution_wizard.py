from odoo import fields, models, api,_
import datetime
from odoo.exceptions import ValidationError


class CompleteExcWizards(models.TransientModel):
    _name = 'tc_exc_complete_wizard'
    _description = 'Test Case Complete Execution Wizard'


    test_case_exec_id = fields.Many2one('kw_test_case_exec', string='Test Case Execution', required=True)
    complete_msg = fields.Char()
    complete_msg1 = fields.Char()
    ok_btn_bool = fields.Boolean()

    def complete_exc(self):
        records = self.env['kw_test_case_exec'].sudo().search([
            ('testing_level', '=', self.test_case_exec_id.testing_level.id),
            ('project_id', '=', self.test_case_exec_id.project_id.id),
            ('module_id', '=', self.test_case_exec_id.module_id.id)
        ])
        for rec in records:
            for line in rec.data_line_ids:
                all_bugs_closed = (not line.bug_ids) or all(bug.state == 'Closed' for bug in line.bug_ids)
                if all_bugs_closed and line.result.code == 'FAIL' and line.result_readonly_boolean == False:
                    raise ValidationError('No Bug Raised For Failed Result.')
                line.write({
                    'iter_comp_boolean': True,
                    'result_readonly_boolean': not all_bugs_closed
                })

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Iteration Completed Successfully.',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

        
       