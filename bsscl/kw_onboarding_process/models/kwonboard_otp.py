# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math, random, string
import datetime
import pytz
import http.client
import json
import smtplib
import requests
from odoo import http


class kw_generated_Otp(models.Model):
    _name = "kw_generate_otp"
    _description = "A model to generate and send otp."

    user = fields.Char(string="User Name")
    mobile_no = fields.Char(string="Mobile Number")
    otp = fields.Char(string="One time password(OTP)")
    exp_date_time = fields.Datetime(string="Expiry Datetime")

    @api.model
    def create(self, vals):
        new_record = super(kw_generated_Otp, self).create(vals)
        return new_record

    @api.multi
    def write(self, vals):
        # self.ensure_one()  
        existing_record = super(kw_generated_Otp, self).write(vals)
        return existing_record
