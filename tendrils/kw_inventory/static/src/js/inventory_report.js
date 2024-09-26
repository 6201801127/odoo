odoo.define('kw_inventory.kw_inventory_report', function (require) {
    "use strict";
    
    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    
    var _t = core._t;
    var _lt = core._lt;

    
    var inventoryReport = AbstractAction.extend(ControlPanelMixin, {
        events: {
            'click #search_by_date': 'filter_table',
        },
        init: function(parent, value) {
            this._super(parent, value);
            var report = [];
            var self = this;
            if (value.tag == 'kw_inventory.kw_inventory_report') {
            }
        },
        willStart: function() {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function() {
            var self = this;
            self.render();
            return this._super();
        },
        
        render: function() {
            var super_render = this._super;
            var self = this;
            
            var inve_report = QWeb.render( 'kw_inventory.kw_inventory_report', {
                widget:self,
            });
            $(inve_report).prependTo(self.$el);
            
            // console.log(inve_report);
            return inve_report;
        },
        renderTables: function() {
            var self = this;
            self.dt_table = $('#search_report').DataTable( {
                // scrollX: true,
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel',
                    {
                        extend: 'pdf',
                        footer: 'true',
                        orientation: 'landscape',
                        title:'Employee Details',
                        text: 'PDF',
                        exportOptions: {
                            modifier: {
                                selected: true
                            }
                        }
                    },
                    {
                        extend: 'print',
                        exportOptions: {
                        columns: ':visible'
                        }
                    },
                ],
              
            } );
        },
        filter_table: function(){
            var self = this;
            var from = $('#fromDate').val();
            var to = $('#toDate').val();
            if ($("#fromDate").val() === "" || $("#toDate").val() === "") {
                alert('Please Select From date and To Date');
                return false;
            }
            var params = {
                fromdate: from,
                 todate:to
                };
            console.log(params);
            self._rpc({
                model: 'kw_inventory_report',
                method: 'action_report_inventory',
                args: [params],
            }).then(function(result){
                console.log(result);
                console.log(self.dt_table);
                if (result!="None"){
                    typeof self.dt_table != 'undefined' ? self.dt_table.destroy() : '';
                    $('#search_report').empty();
                    $("div#date_filter").after("\
                        <div class='d-flex justify-content-center mt-3'>\
                            <div class='table-responsive'>\
                            <table class='table table-hover table-bordered' id='search_report'>\
                                <thead style='background: #108fbb; color: #fff;'>\
                                    <th class='text-center text-capitalize'> requisition number </th>\
                                    <th class='text-center text-capitalize'> pr create date </th>\
                                    <th class='text-center text-capitalize'> requisition Department </th>\
                                    <th class='text-center text-capitalize'> requisition status </th>\
                                    <th class='text-center text-capitalize'> pr approved by </th>\
                                    <th class='text-center text-capitalize'> indent number </th>\
                                    <th class='text-center text-capitalize'> Indent create Date </th>\
                                    <th class='text-center text-capitalize'> Indent Department </th>\
                                    <th class='text-center text-capitalize'> indent status </th>\
                                    <th class='text-center text-capitalize'> indent approved by </th>\
                                    <th class='text-center text-capitalize'> quotation number </th>\
                                    <th class='text-center text-capitalize'> Quotation create Date </th>\
                                    <th class='text-center text-capitalize'> Quotation Status </th>\
                                    <th class='text-center text-capitalize'> quotation approved by </th>\
                                </thead>\
                                <tbody> </tbody>\
                            </table>\
                            </div>\
                        </div>\
                    ");
                    result.forEach(function (item) {
                        $('tbody').append("<tr>\
                            <td class='text-center'>"+item[0]+"</td>\
                            <td class='text-center'>"+item[1]+"</td>\
                            <td class='text-center'>"+item[2]+"</td>\
                            <td class='text-center'>"+item[3]+"</td>\
                            <td class='text-center'>"+item[4]+"</td>\
                            <td class='text-center'>"+item[5]+"</td>\
                            <td class='text-center'>"+item[6]+"</td>\
                            <td class='text-center'>"+item[7]+"</td>\
                            <td class='text-center'>"+item[8]+"</td>\
                            <td class='text-center'>"+item[9]+"</td>\
                            <td class='text-center'>"+item[10]+"</td>\
                            <td class='text-center'>"+item[11]+"</td>\
                            <td class='text-center'>"+item[12]+"</td>\
                            <td class='text-center'>"+item[13]+"</td>\
                            </tr>");
                    });
                    self.renderTables();
                }
                else{
                    $('#search_report').empty();
                }
                
            });
        },
        
        reload: function () {
            window.location.href = this.href;
        },
    });
    core.action_registry.add('kw_inventory.kw_inventory_report', inventoryReport);
    return inventoryReport
});
