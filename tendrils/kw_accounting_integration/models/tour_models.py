# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


def set_journal_sequence_code(self, journal_id):
	""" 
		This sets sequence code to selected journal_id's
		sequence.
	"""
	cur_journal = self.env['account.journal'].sudo().browse(journal_id.id)
	cur_journal_seq = self.env['ir.sequence'].sudo().browse(cur_journal.sequence_id.id)
	seq_dict = {'INV Sequence': 'customer.inv', 'BILL Sequence': 'vendor.bill', 
				'MISC Sequence': 'misc.operation', 'EXCH Sequence': 'exch.diff', 
				'BNK1 Sequence': 'bank', 'CSH1 Sequence': 'cash', 
				'CABA Sequence': 'cash.basis.tax'}
	seq_code = seq_dict.get(cur_journal_seq.name)
	if seq_code:
		cur_journal_seq.write({'code': seq_code})
	return seq_code

def get_partner(self, employee_id, rec_partner=None):
	"""
		This searches for partner_id of an provided employee 
	"""

	rec_user = self.env['hr.employee'].sudo().search([('id', '=', employee_id.id)]).user_id
	if rec_user:
		rec_partner = self.env['res.users'].sudo().search([('id', '=', rec_user.id)]).partner_id
	return rec_partner

class KwTourInherit(models.Model):
	_inherit = 'kw_tour'


	journal_id = fields.Many2one('account.journal', 'Journal')
	account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)


	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		current_employee_id = self.env.user.employee_ids
		if self._context.get('access_label_check'):
            
			if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk'):
				args += ['&','|',('cancellation_id','=',False),('cancellation_id.state','not in',['Applied','Approved']),
                            '|', ('state', '=', 'Approved'), 
                            '|',
                            '&',('state', '=', 'Forwarded'),('final_approver_id.user_id', '=', self.env.user.id),
                            '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id)
                             ]
            
			elif self.env.user.has_group('kw_tour.group_kw_tour_finance'):
				args += ['&','|',('cancellation_id','=',False),('cancellation_id.state','not in',['Applied','Approved']),
                            '|', ('state', 'in', ['Traveldesk Approved', 'Finance Approved']), 
                            '|',
                            '&',('state', '=', 'Forwarded'),('final_approver_id.user_id', '=', self.env.user.id),
                            '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id)
                             ]
			else:
				args += ['&','|',('cancellation_id','=',False),('cancellation_id.state','not in',['Applied','Approved']),
                            '|',
                            '&',('state', '=', 'Forwarded'),('final_approver_id.user_id', '=', self.env.user.id),
                            '&', ('state', '=', 'Applied'), ('employee_id.parent_id.user_id', '=', self.env.user.id)
                            ]

		if self._context.get('filter_tour'):
			if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk') or self.env.user.has_group('kw_tour.group_kw_tour_finance') or self.env.user.has_group('kw_tour.group_kw_tour_admin'):
				args += [('state', '!=', 'Draft')]
			else:
				args += ['&',('state', '!=', 'Draft'),'|',('create_uid','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]

		return super()._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid, is_integrated=True)


	@api.multi
	def post_journal_entry(self):
		for rec in self:

			rec_partner = get_partner(self, rec.employee_id)
			line_id_vals = []
			tour_adv_account = self.env['kw_tour_accounting_configuration'].sudo().search([('code','=','ta')]).account_id
			disbursed_amount = rec.disbursed_inr if rec.disbursed_inr > 0 else rec.disbursed_usd * rec.exchange_rate

			for r in range(2):
				if r == 1 and tour_adv_account:
					line_id_vals.append([0, 0, {
						'account_id': tour_adv_account.id,
						'partner_id': rec_partner.id if rec_partner else False,
						'department_id': rec.employee_id.department_id.id,
						'debit': disbursed_amount,
						'analytic_account_id': self.env['account.analytic.account']\
													.search([('project_id', '=', rec.project_id.id)]).id\
													if rec.tour_type_id.code == 'project' else False
					}])
				else:
					line_id_vals.append([0, 0, {
						'account_id': rec.journal_id.default_credit_account_id.id,
						'credit': disbursed_amount
					}])

			# Setting sequence code of Journal Entry
			if rec.journal_id:
				seq_code = set_journal_sequence_code(self, rec.journal_id) 

				# Creating journal entry
				account_move_id = self.env['account.move'].sudo().create({
					'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
					'date': date.today(),
					'journal_id': rec.journal_id.id,
					'ref': f'{rec.employee_id.display_name} - Tour',
					'tour_type_id': rec.tour_type_id.id,
					'tour_purpose': rec.purpose,
					'project_id': rec.project_id.id if rec.tour_type_id.code == 'project' else False,
					'line_ids': line_id_vals,
				})
				rec.write({'state': 'Posted', 'account_move_id': account_move_id.id})
				self.env.user.notify_success(message='Journal entry has been created!')

		return self.return_to_tour_take_action()


class KwTourAdvanceRequestInherit(models.Model):
	_inherit = 'kw_tour_advance_request'


	journal_id = fields.Many2one('account.journal', 'Journal')
	account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
	finance_access = fields.Boolean(string="Finance Access", compute="_compute_approve")

	@api.multi
	def _compute_approve(self):
		for record in self:
			if self.env.user.has_group('kw_tour.group_kw_tour_admin'):
				record.admin_access = True
			if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk'):
				record.travel_desk_access = True
			if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
				record.finance_access = True

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		if self._context.get('access_check'):
			employee_id = self.env.user.employee_ids

			if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
				args += ['|', ('state', 'in', ['Approved', 'Grant']),'&',('state', 'in', ['Applied']), ('employee_id.parent_id', 'in', employee_id.ids)]
			else:
				args += [('state', 'in', ['Applied']), ('employee_id.parent_id', 'in', employee_id.ids)]
		if self._context.get('filter_advance_request'):
			if self.env.user.has_group('kw_tour.group_kw_tour_finance'):
				args += []
			else:
				args += ['|',('create_uid','=',self.env.user.id),('employee_id.parent_id.user_id','=',self.env.user.id)]
		return super()._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid, is_integrated=True)


	def post_journal_entry(self):
		for rec in self:

			rec_partner = get_partner(self, rec.employee_id)
			line_id_vals = []
			tour_adv_account = self.env['kw_tour_accounting_configuration'].sudo().search([('code','=','ta')]).account_id
			to_be_given_amount = rec.to_be_given_inr if rec.to_be_given_inr > 0 else rec.to_be_given_usd * rec.new_exchange_rate

			for r in range(2):
				if r == 1 and tour_adv_account:
					line_id_vals.append([0, 0, {
						'account_id': tour_adv_account.id,
						'partner_id': rec_partner.id if rec_partner else False,
						'department_id': rec.employee_id.department_id.id,
						'debit': to_be_given_amount,
						'analytic_account_id': self.env['account.analytic.account']\
													.search([('project_id', '=', rec.tour_id.project_id.id)]).id\
													if rec.tour_type_id.code == 'project' else False
					}])
				else:
					line_id_vals.append([0, 0, {
						'account_id': rec.journal_id.default_credit_account_id.id,
						'credit': to_be_given_amount
					}])

			# Setting sequence code of Journal Entry
			if rec.journal_id:
				seq_code = set_journal_sequence_code(self, rec.journal_id)

				# Creating journal entry
				account_move_id = self.env['account.move'].sudo().create({
					'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
					'date': date.today(),
					'journal_id': rec.journal_id.id,
					'ref': f'{rec.employee_id.display_name} - Advance',
					'tour_type_id': rec.tour_id.tour_type_id.id,
					'tour_purpose': rec.tour_id.purpose,
					'project_id': rec.tour_id.project_id.id if rec.tour_id.tour_type_id.code == 'project' else False,
					'line_ids': line_id_vals,
				})
				rec.write({'state': 'Posted', 'account_move_id': account_move_id.id})
				self.env.user.notify_success(message='Journal entry has been created!')

		return self.return_to_adv_req_take_action()


class KwTourSettlementInherit(models.Model):
	_inherit = 'kw_tour_settlement'

	@api.model
	def _get_domain(self):
		settlement_pending_tour_ids = self.env['kw_tour_settlement'].search([('create_uid','=',self._uid),('state','!=','Rejected')])
		tour_ids = settlement_pending_tour_ids.mapped('tour_id').ids
		return [('create_uid','=',self._uid),('id','not in',tour_ids),
				('state','in',['Approved','Traveldesk Approved','Finance Approved','Posted']),('settlement_id','=',False)]


	journal_id = fields.Many2one('account.journal', 'Journal')
	tour_id = fields.Many2one('kw_tour', 'Tour', ondelete='cascade', required=True, domain=_get_domain)
	account_move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)


	def post_journal_entry(self):
		for rec in self:

			rec_partner = get_partner(self, rec.employee_id)
			line_id_vals = []
			tour_adv_account = self.env['kw_tour_accounting_configuration'].sudo().search([('code','=','ta')]).account_id
			project_exp_account = self.env['kw_tour_accounting_configuration'].sudo().search([('code','=','pe')]).account_id
			# advance_amount = rec.advance_inr if rec.advance_inr > 0 else rec.advance_usd * rec.tour_id.exchange_rate
			expenditure_amount = rec.total_domestic if rec.total_domestic > 0 else rec.total_international * rec.tour_id.exchange_rate
			# payable_amount = rec.paid_domestic if rec.paid_domestic != 0 else rec.paid_international * rec.tour_id.exchange_rate
			# receivable_amount = rec.receivable_inr if rec.receivable_inr != 0 else rec.receivable_usd * rec.tour_id.exchange_rate

			# Tour advance credit transaction
			if tour_adv_account:
				line_id_vals.append([0, 0, {
					'account_id': tour_adv_account.id,
					'partner_id': rec_partner.id if rec_partner else False,
					'department_id': rec.employee_id.department_id.id,
					'credit': expenditure_amount,
					'analytic_account_id': self.env['account.analytic.account']\
												.search([('project_id', '=', rec.tour_id.project_id.id)]).id\
												if rec.tour_id.tour_type_id.code == 'project' else False
				}])

			# Project expense debit transaction
			if project_exp_account:
				line_id_vals.append([0, 0, {
					'account_id': project_exp_account.id,
					'partner_id': rec_partner.id if rec_partner else False,
					'department_id': rec.employee_id.department_id.id,
					'debit': expenditure_amount,
					'analytic_account_id': self.env['account.analytic.account']\
												.search([('project_id', '=', rec.tour_id.project_id.id)]).id\
												if rec.tour_id.tour_type_id.code == 'project' else False
				}])

			# Employee to pay Organisation
			# if payable_amount < 0:
			# 	line_id_vals.append([0, 0, {
			# 		'account_id': rec.journal_id.default_credit_account_id.id,
			# 		'debit': abs(payable_amount)
			# 	}])
			# else:
			# 	line_id_vals.append([0, 0, {
			# 		'account_id': rec.journal_id.default_credit_account_id.id,
			# 		'credit': receivable_amount
			# 	}])

			# Setting sequence code of Journal Entry
			if rec.journal_id:
				seq_code = set_journal_sequence_code(self, rec.journal_id)

				# Creating journal entry
				account_move_id = self.env['account.move'].sudo().create({
					'name': self.env['ir.sequence'].next_by_code(seq_code) if seq_code else '/',
					'date': date.today(),
					'journal_id': rec.journal_id.id,
					'ref': f'{rec.employee_id.display_name} - Settlement',
					'tour_type_id': rec.tour_id.tour_type_id.id,
					'tour_purpose': rec.tour_id.purpose,
					'project_id': rec.tour_id.project_id.id if rec.tour_id.tour_type_id.code == 'project' else False,
					'line_ids': line_id_vals,
				})
				rec.write({'state': 'Posted', 'account_move_id': account_move_id.id})
				self.env.user.notify_success(message='Journal entry has been created!')

		return self.return_to_settlement_take_action()

class AccountingConfiguration(models.Model):
	_name = "kw_tour_accounting_configuration"


	name = fields.Char('Name')
	code = fields.Char('Code')
	active = fields.Boolean('Active', default=True)
	account_id = fields.Many2one('account.account', 'Account')


	@api.constrains('name', 'code')
	def check_constrains(self):
		for rec in self:
			record = self.env['kw_tour_accounting_configuration'].sudo().search([('name','=',rec.name), ('code','=',rec.code)]) - self
			if record:
				raise ValidationError(f'{rec.name} with code {rec.code} already exists.')


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    tour_type_id = fields.Many2one('kw_tour_type', 'Type of Tour')
    tour_purpose = field_name = fields.Text('Purpose')
    project_id = fields.Many2one('crm.lead', string='Project')