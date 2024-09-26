from odoo.exceptions import ValidationError
from odoo import models, fields, api


class BugLifeCyclePolicyMenuWizard(models.TransientModel):
    _name = 'bug_life_cycle_open_menu'
    _description = 'Open  policy Details when click module'


    data = fields.Text('Data', default="""
    TEST LEAD Responsibilities.

        • Tagging user with their roles. As doing in TEST LAB. (Refer User Tagging Add & View.png files)
        • Creation Module Name. (With Tool Tips: Menu, Global Link etc. during creation time).  
        • Creation Sub Module Name. (With Tool Tips: Sub Menu, Primary Link etc. during creation time). 
        • Creation of Screen/Tab Name(Optional)
        • Comment/Discussion on Rejected defect.(Mandatory)
        • Developer/Module Lead List for the project.(Mandatory)

    TESTER Responsibilities.

        • Adequate information with the bug. Snap + Steps to reproduce the defect + Test Data + Proper Navigation.
        • Proper closing proof (.pdf/.png/.jpg/.mp4 with audio/text/ up to maximum size possible) of a defect.
        • Understand the SLA. So, FIXED defect need to be retested/commented within the SLA.
        • Need leave and get it approved leaves ASAP before 11 AM. So that escalation mail will be not received on delay re testing for defect.
        • Tester will be allowed to mark Close on Rejected defect. If TEST LEAD allowed through configuration.

    MODULE/TECH LEAD Responsibilities.

        • ASAP Assignment of the bug
        • Editing priority severity. Else severity will be treated accepted what has been logged by Tester/Test Lead 
        • Strong Analysis before putting a defect into Rejection or Hold.
        • FIXED means “Fixed and synced to Test Server”. This is to be train to his developer. It will be clear go ahead for re-testing.
        • Plan, Assign and expect the developer with 7 to 7.5 hours of development task. Rest 1 to 1.5 hours developer should do UNIT testing/Bug fixing. 


    DEVELOPER Responsibilities

        • Careful and patiently reading the information provided before asking clarification on bug to TESTER Or TEST LEAD. N.B. For Tester/Test Lead i) Steps to reproduce the defect, ii) Snapshot and iii) navigation iv) Test Data etc.…. are some mandatory information those has to be filled before logging defect. So, defect will be itself comprehensive. 
        • Understand the SLA. Need leave and get it approved leaves ASAP before 11 AM. So that escalation mail will be not received on delay in FIXING Or Acknowledging defect.
        • Fixing defect without side effect on working functionality.
    
    
    """, readonly=True)
    check_responsibilities = fields.Boolean(string='Check Response', required=True)

    def submit_policy_rule_btn(self):
        if self.check_responsibilities is not True:
            raise ValidationError("Please read and check.")
        action_id = self.env.ref('kw_bug_life_cycle.kw_bug_life_cycle_conf_action_dashboard').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_bug_life_cycle_conf&view_type=kanban',
            'target': 'self',
        }

