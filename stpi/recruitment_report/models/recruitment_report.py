from odoo import fields,api,models
import math
from datetime import datetime, timedelta
from pytz import timezone, UTC


class LateComingReport(models.Model):
    _name="recruitment.report"
    _description="Recruitment Report"



    jobposition = fields.Char(string="Job Position")
    department = fields.Char(string="Department")
    branch = fields.Char(string="Center")
    sanctionedpositions = fields.Integer(string="Sanctioned Positions")
    currentempcount = fields.Integer(string="Current EMP count")
    scpercet = fields.Float(string="SC Percent")
    stpercet = fields.Float(string="ST Percent")
    obcpercet = fields.Float(string="OBC Percent")
    ebcpercet = fields.Float(string="EBC Percent")
    vhpercent = fields.Float(string="VH Percent")
    phpercent = fields.Float(string="PH Percent")
    hhpercent = fields.Float(string="HH Percent")
    ruleclass = fields.Char(string="Rule Class")
    nosc = fields.Float(string="No SC")
    nost = fields.Float(string="No ST")
    noobc = fields.Float(string="No OBC")
    noebc = fields.Float(string="No EBC")
    currobc = fields.Float(string="Current OBC")
    currgen = fields.Float(string="Current General")
    currsc = fields.Float(string="Current SC")
    currst = fields.Float(string="Current ST")
    currewc = fields.Float(string="Current EWC")


    def get_recruitment_report(self):
        return self.env['recruitment.report'].search([])

