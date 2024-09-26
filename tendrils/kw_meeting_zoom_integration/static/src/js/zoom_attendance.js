odoo.define('kw_meeting_zoom_integration.zoom_attendance_report', function (require) {
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

    var ZoomAttendanceView = AbstractAction.extend(ControlPanelMixin, {
        dt_table:false,
        init: function(parent, value) {
            this._super(parent, value);
            var self = this;
            self.render();
//            if (value.tag == 'kw_meeting_zoom_integration.zoom_attendance_report') {
//                ajax.jsonRpc("/get_checklist_report", 'call')
//                .then(function(result){
//                    self.post_onboard_checklist = result
//                }).done(function(){
//                    self.render();
//                    self.href = window.location.href;
//                });
//            }
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
            var kw_meeting_zoom_attendance = QWeb.render('kw_meeting_zoom_integration.zoom_attendance_report', {widget: self});
            $( ".o_control_panel" ).addClass( "o_hidden" );
            setTimeout(function(){
                $(kw_meeting_zoom_attendance).prependTo(self.$el);
//                console.log(self.$el)
                self.fetch_data('render');
            },2000)
            return kw_meeting_zoom_attendance
        },
        fetch_data: function(mode){
            var self = this;
            $('#meeting_attendance_list').addClass('o_hidden');
            $("#meeting_attendance_list_no_record").addClass('o_hidden');
            $("#meeting_attendance_list_loader").fadeIn();
            return rpc.query({
                    model: 'kw_meeting_events',
                    method: 'get_report_data'
                }).then(function(result){
//                    console.log(result)
                    self.initTable(result, mode);
                });
        },
        initTable: function(result, mode){
            var mode = mode || ''
            var self = this
            var noorderable = new Array();
            if($.isEmptyObject(result)){
                $("#meeting_attendance_list_no_record").removeClass('o_hidden');
            }else{
                $('#meeting_attendance_list').removeClass('o_hidden');
                var dataSet = new Array();
                var columns = new Array();
                $.each(result, function(key, val){
                    if(key == 'columns'){
                        $.each(val, function(key1, val1){
                            $.each(val1, function(key2, val2){
                                columns.push({ title: val2 });
                            });
                            if(key1 > 4){
                                noorderable.push(key1);
                            }
                        });
                    }else{
                        $.each(val, function(key1, val1){
                            var tempArr = new Array();
                            $.each(val1, function(key2, val2){
                                tempArr.push(val2);
                            });
                            dataSet.push(tempArr);
                        });
                    }
                });

                if(self.dt_table){
                    self.dt_table.destroy();
                }

                self.dt_table = $('#meeting_attendance_list').DataTable({
                    responsive: true,
                    "paging": false,
                    "order": [],
//                    "fixedHeader": true,
                    "bFilter": false,
                    "dom": 't',
                    "data": dataSet,
                    "columns": columns,
                    "buttons": [
                        'excel',
                    ],
                    'headerCallback':function(thead, data, start, end, display){
                        $(thead).find('th:gt(4)').each(function(){
                            $(this).html(moment($(this).html()).format('DD-MMM-YYYY'));
                        });
                    },
                    'rowCallback': function(row, data, index){
                        $.each(data, function(key, val){
                            if(key > 4){
                                if(val == true){
                                    $(row).find('td:eq('+key+')').css({'background-color': '#a9d08d', 'color': '#a9d08d'});
                                }else if(val == false){
                                    $(row).find('td:eq('+key+')').css({'background-color': '#ff696a', 'color': '#ff696a'});
                                }
                            }
                        });
                    },
                    "columnDefs": [
                        { "width": "7%", "targets": 0 },
                        { "width": "7%", "targets": 1 },
                        { "width": "5%", "targets": 2, "className": "text-center" },
                        { "width": "5%", "targets": 3, "className": "text-center" },
                        { "width": "5%", "targets": 4, "className": "text-center" },
                        { "orderable": false, "targets": noorderable }
                      ]
                });
            }
            $("#meeting_attendance_list_loader").hide();
        },

        reload: function () {

            window.location.href = this.href;
        },

    });
    core.action_registry.add('kw_meeting_zoom_integration.zoom_attendance_report', ZoomAttendanceView);

    return ZoomAttendanceView
   });
