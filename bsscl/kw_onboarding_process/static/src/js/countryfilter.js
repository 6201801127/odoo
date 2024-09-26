odoo.define('kw_onboarding_process.kwonboard_personal_detail', function (require) {  // how it works ??
    'use strict';
    
    $(function () {
        $('#ddlPresentContry').on("change", function(){
            var country_id = $('#ddlPresentContry').val();
            var ajax = require('web.ajax');
                ajax.jsonRpc("/countryfilter", 'call', {'country_id' :country_id})
                    .then(function (values) {
                        
                        if (values !="None"){
                            $("#ddlPresState").empty()
                            $.each( values, function( key, value ) {
                                $("#ddlPresState").append('<option value='+key+'>'+value+'</option>');
                              });
                        } else {
                            $("#ddlPresState").empty()
                            $("#ddlPresState").append('<option value="">Select City</option>');
                        }

                });
           
        });
        
        $('#ddlPermCountry').on("change", function(){
            var country_id = $('#ddlPermCountry').val();
            // console.log(country_id);
            var ajax = require('web.ajax');
                ajax.jsonRpc("/countryfilter", 'call', {'country_id' :country_id})
                    .then(function (values) {
                        if (values !="None"){
                            $("#ddlPermstate").empty()
                            $.each( values, function( key, value ) {
                                $("#ddlPermstate").append('<option value='+key+'>'+value+'</option>');
                              });
                        } else {
                            $("#ddlPermstate").empty()
                            $("#ddlPermstate").append('<option value="">Select City</option>');
                        }
                });
           
        })  
        
        
        $('#chkCopyAddress').on("click", function(){
            if (this.checked) {
                var country_id = $('#ddlPresentContry').val();
                var city = $('#txtPresCity').val();
                var pin = $('#txtPresPin').val();
                var state = $('#ddlPresState').val();
                var pp1 = $('#txtPresAddressLine1').val();
                var pp2 = $('#txtPresAddressLine2').val();
                $('#txtPermCity').val(city);
                $('#txtPermAddressLine1').val(pp1);
                $('#txtPermAddressLine2').val(pp2);
                $('#ddlPermstate').val(state);
                $('#txtPermPinCode').val(pin);
                console.log(country_id,city);
                var ajax = require('web.ajax');
                    ajax.jsonRpc("/countryfilter", 'call', {'country_id' :country_id})
                        .then(function (values) {
                            var selected;
                            if (values !="None"){
                                var state_selected = $("#ddlPermstate").attr('data-select');
                                $("#ddlPermstate").empty();
                                $.each( values, function( key, value ) {
                                    selected = key ===  state_selected ? 'selected' : '';
                                    $("#ddlPermstate").append('<option value='+key+' '+selected+'>'+value+'</option>');
                                });
                                $("#ddlPermstate").select2();
                            } else {
                                $("#ddlPermstate").empty()
                                $("#ddlPermstate").append('<option value="">Select City</option>');
                            }

                    });
            } 
           
        }) 
    
    }); 
    
});