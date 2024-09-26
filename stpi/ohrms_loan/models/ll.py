@api.multi
def compute_installment(self):
    """This automatically create the installment the employee need to pay to
    company based on payment start date and the no of installments.
        """
    for loan in self:
        fcb_in = 0.00
        new_ins = 0.00
        closing_balance = 0.00
        loan.loan_lines.unlink()
        date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
        if loan.installment < loan.type_id.threshold_emi:
            cur_ins = loan.installment - loan.type_id.threshold_below_emi
            new_ins = loan.type_id.threshold_below_emi
        elif loan.installment > loan.type_id.threshold_emi:
            cur_ins = loan.installment - loan.type_id.threshold_above_emi
            new_ins = loan.type_id.threshold_above_emi
        else:
            cur_ins = loan.installment

        if loan.installment <= 0:
            raise UserError(_('Please enter Number of Installment grater than Zero'))
        if loan.loan_amount <= 0:
            raise UserError(_('Please enter Loan Amount grater than Zero'))

        if cur_ins > 0:
            amount = loan.loan_amount / cur_ins
        else:
            amount = loan.loan_amount

        for i in range(1, cur_ins + 1):
            cb_interest = 0.0
            for j in range(0, i):
                # print('-----j',j)
                cb_interest += ((loan.loan_amount - (amount * (j))) * (self.interest / 100)) / 12
                fcb_in = cb_interest

            closing_balance = loan.loan_amount - amount * i
            year_interest = (loan.loan_amount - (amount * (i - 1))) * (self.interest / 100)
            monthly_interest = year_interest / 12
            self.env['hr.loan.line'].create({
                'date': date_start,
                'principle_recovery_installment': amount,
                'closing_blance_principle': closing_balance,
                'yearly_interest_amount': year_interest,
                'monthly_interest_amount': monthly_interest,
                'cb_interest': cb_interest,
                'pending_amount': closing_balance + monthly_interest,
                'amount': amount + monthly_interest,
                'employee_id': loan.employee_id.id,
                'loan_id': loan.id})
            date_start = date_start + relativedelta(months=1)

        if closing_balance == 0.00:
            for k in range(1, new_ins + 1):
                cb_int = fcb_in / new_ins
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'principle_recovery_installment': cb_int,
                    'closing_blance_principle': 0.00,
                    'yearly_interest_amount': 0.00,
                    'monthly_interest_amount': 0.00,
                    'cb_interest': 0.00,
                    'pending_amount': 0.00,
                    'amount': 0.00,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
    return True