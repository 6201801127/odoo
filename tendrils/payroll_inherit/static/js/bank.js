odoo.define('payroll_inherit.update_bank_details_web_template', function (require) {
    'use strict';
    var bank = {
        init: function () {
            $('#submitBankDetails').click(function (e) {
                var bank_id = $("#bank_names").val()
                var ifsc = $("#bank_names option:selected").attr('ifsc');
                if (bank_id == null)
                {
                    swal("Please Select The Bank!");
                    return false
                }
                var bank_account_number = $("#bank_account_number").val()
                if (bank_account_number == '')
                {
                    swal("Please Fill Up The Bank Number!");
                    return false
                }
                var numbers = /^[0-9]+$/;
                if($("#bank_account_number").val().match(numbers))
                {
                    console.log('aaaa')
                }
                else
                {
                    swal("Please Input Numeric Characters only");
                    return false
                }
                var bankName = $("#bank_names option:selected").text();
                $('#account_number').html(bank_account_number)
                $('#bank_names_res').html(bankName)
                $('#bank_bic').html(ifsc)
                $('#bank_names_res_hidden').val(bank_id)
                $('#bank_bic_hidden').val(ifsc)
                $('#account_number_hidden').val(bank_account_number)
                $('#myModal').modal('show');
                return false;
            });
        },
    };
    $(function() {
        bank.init();  
    });
});
