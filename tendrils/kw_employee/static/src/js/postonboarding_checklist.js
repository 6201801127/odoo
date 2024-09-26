odoo.define('kw_employee.kw_postonboarding_checklist_report', function (require) {
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
    var rpc = require('web.rpc')
    
    var PostOnboardingChecklistView = AbstractAction.extend(ControlPanelMixin, {
        dt_table:false,
        month:moment().format("M"),
        year:moment().format("YYYY"),
        hs:{},
        dep:false,
        div:false,
        sec:false,
        pra:false,
        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
//            var employee_data = [];
            if (value.tag == 'kw_employee.kw_postonboarding_checklist_report') {
//                self.render();
//                self.href = window.location.href;
                ajax.jsonRpc("/get_checklist_report", 'call')
                .then(function(result){
                    self.post_onboard_checklist = result
                }).done(function(){
                    self.render();
                    self.href = window.location.href;
                    //  self.show_report();
                    //self.render_Datatable();
                });
                $(document).on('click','#search_checklist_report', function(){
                    self.fetch_data('search');
                }).on('change', 'select[id^=onboarding_checklist_]', function(){
                    self.fetch_dept($(this));
                    self.getHash();
                });
            }
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
            var kw_post_onboard_checklist = QWeb.render('kw_employee.kw_postonboarding_checklist_report', {widget: self});
            $( ".o_control_panel" ).addClass( "o_hidden" );
            $(kw_post_onboard_checklist).prependTo(self.$el);

            $('#onboarding_chcklist_month').val(self.month);
            $('#onboarding_chcklist_year').val(self.year);

            self.fetch_data('render');
            self.fetch_dept();

            return kw_post_onboard_checklist
        },
        fetch_data: function(mode){
            var self = this;
            $('#post_onboard_checklist').addClass('o_hidden');
            $("#post_onboard_checklist_no_record").addClass('o_hidden');
            $("#post_onboard_checklist_loader").fadeIn();
            return rpc.query({
                    model: 'kw_employee_onboarding_checklist',
                    method: 'get_report_data',
                    args: [{
                        month: $('#onboarding_chcklist_month').val(),
                        year:  $('#onboarding_chcklist_year').val(),
                        dept_id:  $('#onboarding_checklist_department').val(),
                        div_id:  $('#onboarding_checklist_division').val(),
                        sec_id:  $('#onboarding_checklist_section').val(),
                        pra_id:  $('#onboarding_checklist_practice').val(),
                    }]
                }).then(function(result){
                    console.log(result)
                    self.initTable(result, mode);
                });
        },
        initTable: function(result, mode){
            var mode = mode || ''
            var self = this
            if($.isEmptyObject(result)){
                $("#post_onboard_checklist_no_record").removeClass('o_hidden');
            }else{
                $('#post_onboard_checklist').removeClass('o_hidden');
                var dataSet = new Array();
                var columns = new Array();
                $.each(result, function(key, val){
                    if(key == 'name'){
                        $.each(val, function(key1, val1){
                            columns.push({ title: val1 });
                        });
                    }else{
                        var tempArr = new Array();
                        $.each(val, function(key1, val1){
                            tempArr.push(val1);
                        });
                        dataSet.push(tempArr);
                    }
                });
                if(self.dt_table){
                    self.dt_table.destroy();
                }
                self.dt_table = $('#post_onboard_checklist').DataTable({
                    // responsive: true,
                    "paging": false,
                    "fixedHeader": true,
                    "bFilter": false,
                    "dom": 't',
                    "data": dataSet,
                    "columns": columns,
                    "fixedColumns" :   {
                        leftColumns: 1
                    },
                    "buttons": [
                        'excel',
                    ],
                    'rowCallback': function(row, data, index){
                        $.each(data, function(key, val){
                            if(val == 'Yes'){
                                $(row).find('td:eq('+key+')').css('background-color', '#99cee1');
                            }else if(val == 'No'){
                                $(row).find('td:eq('+key+')').css('background-color', '#ee9ca2');
                            }
                        });

                        $(row).find('td').addClass('pt-0 pb-0');
                        $(row).find('td:gt(0)').addClass('text-center');
                    },
                    "columnDefs": [
                        { "width": "20%", "targets": 0 }
                      ]
                });
            }
            $("#post_onboard_checklist_loader").hide();
        },
        reload: function () {
            window.location.href = this.href;
        },
        fetch_dept: function(_el){
            //return true
            var self = this;
            var el = _el || false;
            var mode = 'department';
            var pid = 0;
            if(el){
                mode = el.attr('rel');
                pid = el.val();
            }
            return rpc.query({
                    model: 'kw_employee_onboarding_checklist',
                    method: 'get_dept_details',
                    args: [{
                        id: pid,
                        type: mode
                    }]
                }).then(function(result){
                    if(!el){
                        $("#onboarding_checklist_department").html($("<option>").html("All").attr("value","0"));
                        $("#onboarding_checklist_division").html("");
                        $("#onboarding_checklist_section").html("");
                        $("#onboarding_checklist_practice").html("");
                    }else{
                        if(mode == 'division'){
                            $("#onboarding_checklist_division").html("");
                            $("#onboarding_checklist_section").html("");
                            $("#onboarding_checklist_practice").html("");
                        }else if(mode == 'section'){
                            $("#onboarding_checklist_section").html("");
                            $("#onboarding_checklist_practice").html("");
                        }else if(mode == 'practice'){
                            $("#onboarding_checklist_practice").html("");
                        }
                        $("#onboarding_checklist_"+mode).html($("<option>").html("All").attr("value","0"));
                    }
                    $.each(result, function(key, val){
                        if(!el){
                            $("#onboarding_checklist_department").append($("<option>").html(val.name).attr("value",val.id));
                        }else{
                            $("#onboarding_checklist_"+mode).append($("<option>").html(val.name).attr("value",val.id));
                        }
                    });
                });
        },
        getHash:function(key){
            self.hs = window.location.hash.split('#')[1].split('&');
            $.each(self.hs, function(k,v){
                console.log(k, v);
            });
        },
        setHash:function(key, val){

        },
    });
    core.action_registry.add('kw_employee.kw_postonboarding_checklist_report', PostOnboardingChecklistView);

    return PostOnboardingChecklistView
   });
