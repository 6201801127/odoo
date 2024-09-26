odoo.define('kw_sale.company_target_plan', function (require) {
    "use strict";

    var core = require('web.core');
    var framework = require('web.framework'); var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');

    var CompanyTargetPlan = AbstractAction.extend(ControlPanelMixin, {
        el:$('#company_target_body').find('tr.row-0').clone(),
        multipliers: {'apr':12, 'may':11, 'jun':10, 'jul':9, 'aug':8, 'sep':7, 'octo':6, 'nov':5, 'dec':4, 'jan':3, 'feb':2, 'mar':1},
        events: {
            'change #target_fiscal_year': _.debounce(function(){
                var self = this;
                self.selected_fiscal_year = $('#target_fiscal_year').val();
                self.fetch_data('clear');
            }),
            'change input[name^="work_"]:not(:last)': _.debounce(function(e, f){
                this.computeTotal($(e.target).attr('name').split("_")[0]);
            }),
            'change input[name^="bill_"]:not(:last)': _.debounce(function(e, f){
                this.computeTotal($(e.target).attr('name').split("_")[0]);
            }),
            'change input[name^="coll_"]:not(:last)': _.debounce(function(e, f){
                this.computeTotal($(e.target).attr('name').split("_")[0]);
            }),
        },
        computeTotal: function(prefix){
            var t = 0;
            console.log(prefix);
            $('input[name^="'+prefix+'_"]:not(:last)').each(function(){
                console.log($(this).val());
                t += $(this).val() != '' ? parseInt($(this).val()) : 0 ;
            });
            $('input[name="'+prefix+'_total"]').val(t);
        },
        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            self.render();
//            setTimeout(function(){
//            $('input[name^="work_"]:not(:last), input[name^="bill_"]:not(:last), input[name^="coll_"]:not(:last)').change(function(){
//                var prefix = $(this).attr('name').split("_")[0];
//                var t = 0;
//                $('input[name^="'+prefix+'_"]:not(:last)').each(function(){
//                    t+=parseInt($(this).val());
//                });
//                $('input[name="'+prefix+'_total"]').val(t);
//            });}, 1000);
        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            return this._super();
        },
        render: function() {
            var self = this;
            var target_plan = QWeb.render('kw_sale.company_target_plan', {widget: self});
            $( ".o_control_panel" ).addClass( "o_hidden" );
            setTimeout(function(){
                $(target_plan).prependTo(self.$el);
                self.fetch_data('render');
                self.fetch_fy();
//                $('#btn_company_target_save').on('click',function(){
//                return fetch(self.save_company_target_plan());
//                });
                $('#btn_company_target_save').on('click',function(){
                    swal({
                    title: "Are you sure want to submit?",
                    text: "",
                    content: "hello",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    cancelButtonText: "No",
                    dangerMode: true,
                    buttons: {
                        confirm: { text: 'Yes, Submit', className: 'btn-success' },
                        cancel: 'No'
                    },
                },function (isConfirm) {
                    if (isConfirm) {
                        return fetch(self.save_company_target_plan());
                    } else {
                        swal.close();
                    }
                });
                });
            },2000)
            return target_plan;
        },
        fetch_fy: function(mode){
            var self = this;
            var el = mode || false;
            return rpc.query({
                    model: 'kw_sale_target_master',
                    method: 'get_fy_data',
                }).then(function(result){
                    $.each(result, function(key, val){
                        var selected = val.default_fy ? true : false;
                        if(val.default_fy){
                            self.selected_fiscal_year = val.id;
                        }
                        $("#target_fiscal_year").append($("<option>").html(val.name).attr({"value":val.id, "selected":selected}));
                    });
                    //self.fetch_data('clear');
                });
        },
        fetch_data: function(mode){
            var self = this;
            $("#target_loader_no_record").addClass('o_hidden');
            $("#target_loader").addClass('o_hidden');
//            $("#company_target_table").addClass('o_hidden');
            self.el = $('#company_target_body').find('tr.row-0').clone();
//            return rpc.query({
//                    model: 'kw_recruitment_positions',
//                    method: 'get_resource_data',
//                    args:[],
//                    kwargs: {'selected_fiscal_year': self.selected_fiscal_year}
//                }).then(function(result){
//                    if(result && result[0][0]){
//                        $("#form_target_box").removeClass('o_hidden');
//                        self.initTable(result[0], mode);
//                    }else{
//                        $("#target_loader_no_record").removeClass('o_hidden');
//                    }
//                });
        },
        initTable: function(result, mode){
            var mode = mode || '';
            var self = this;
            var $el = self.el.clone();
            if(mode == 'clear'){
                $('#recr_budget_table').find('tr:gt(0)').remove();
            }
            $.each(result, function(k, rec){
                var key = '';
                $el.find('.designation').attr('data-id',rec.rec_id);
                $el.find('.sl_no').html(parseInt(k)+1);
                $el.find('.designation').html(rec.designation);
                $el.find('.tech').html(rec.tech);
                $el.find('.branch').html(rec.branch);
                $el.find('.budget-amount').attr({'readonly':true, 'name':''}).addClass('border-0');
                $el.find('.budget-resource').html('').removeClass('bg-info');
                if (rec.apr){
                    key = 'apr';
                }else if (rec.may){
                    key = 'may';
                }else if (rec.jun){
                    key = 'jun';
                }else if (rec.jul){
                    key = 'jul';
                }else if (rec.aug){
                    key = 'aug';
                }else if (rec.sep){
                    key = 'sep';
                }else if (rec.octo){
                    key = 'octo';
                }else if (rec.nov){
                    key = 'nov';
                }else if (rec.dec){
                    key = 'dec';
                }else if (rec.jan){
                    key = 'jan';
                }else if (rec.feb){
                    key = 'feb';
                }else if (rec.mar){
                    key = 'mar';
                }
                $el = self.set_field($el, key, rec);
                $el.find('.budget_total').show();
                //$('#recr_budget_table').empty();
                if(k==0){
                    //$('#recr_budget_table').empty();
                    $('#recr_budget_table').append("<tr>"+$el.html()+"</tr>");
                }else{
                    //$('#recr_budget_table').empty();
                    $('#recr_budget_table').append("<tr>"+$el.html()+"</tr>");
                }
                $('input[name=budget_'+rec.rec_id+'_'+key+']').val(rec[key+'_budget']);
            });

            self.compute_budget();
        },
        set_field: function(el, key, rec){
//            console.log('set_field  >> '+ key+' >> ', rec[key+'_budget'] );
            el.find('.budget-res-'+key).html(rec[key]).addClass('bg-info');
            el.find('.budget_'+key).attr({'readonly':false, 'name':'budget_'+rec.rec_id+'_'+key+''}).removeClass('border-0');
//            el.find('td:lt('+el.find('.budget_'+key).parent().index()+')').find('input.budget-amount').hide();
            return el;
        },
        reload: function () {
            window.location.href = this.href;
        },
        compute_budget: function(rec){
            var self = this;
//            console.log('compute_budget');
            $('.budget-amount').on('change',function(){
                var budget_total = 0;
                self.render_budget($(this));
                self.update_final_budget();
            })
            $('.budget-amount[name^="budget_"]').each(function(){
                $(this).trigger('change');
            });
        },
        render_budget:function(el){
            var self = this;
            var budget_total = 0;
            el.closest('tr').find('td:gt('+el.parent().index()+')').find('input:not(.budget_total)').val(el.val());
            budget_total = parseInt(el.val())*parseInt(self.multipliers[el.attr('rel')])
            el.closest('tr').find('td:gt('+el.parent().index()+')').find('input.budget_total').val(budget_total);
        },
        save_company_target_plan: function(){
            var self = this;
            var frm = $('#company_target_table').serializeArray();
            var json_data = JSON.stringify($('#company_target_table').serializeArray());

            console.log('save',json_data);
            var params = {
                'rec':json_data,
                'fiscal_year': self.selected_fiscal_year
            };
            return rpc.query({
                    model: 'kw_sale_target_master',
                    method: 'save_company_target',
                    args: [params],
                    kwargs:params
                }).then(function(result){
                    console.log('result >> '+result)
                });
        },
        update_final_budget: function(){
            var final_total = 0;
            $('input.budget_total').each(function(){
                final_total = final_total + ($(this).val() != '' ? parseInt($(this).val()) : 0);
            });
            $('#span_rec_budget_total').html(final_total);
        },
    });
    core.action_registry.add('kw_sale.company_target_plan', CompanyTargetPlan);

    return CompanyTargetPlan
    });
