odoo.define('kw_resource_management.forecasted_release_report', function (require) {
    'use strict';
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    
    var ForecastedReleaseReport = AbstractAction.extend({
        template: 'ForecastedReleaseReportSheet',
        events: {
            'click td[data-month]': '_onCellClick',
        },
        
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.domain = action.context.domain || [];
        },
        
        start: function() {
            this._super();
            this._renderTable();
        },
        
        _renderTable: function() {
            var self = this;
            rpc.query({
                model: 'forecasted_release_report',
                method: 'search_read',
                args: [self.domain, ['primary_skill_id', 'job_id', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar']],
            }).then(function(records) {
                var aggregatedData = self._aggregateData(records);
                self._renderRows(aggregatedData);
            });
        },
        
        _aggregateData: function(records) {
            var aggregatedData = {};
            records.forEach(function(record) {
                var key = record.primary_skill_id[1] + '-' + record.job_id[1];
                if (!aggregatedData[key]) {
                    aggregatedData[key] = {
                        primary_skill_id: record.primary_skill_id[1] || '',
                        job_id: record.job_id[1] || '',
                        apr: 0,
                        may: 0,
                        jun: 0,
                        jul: 0,
                        aug: 0,
                        sep: 0,
                        oct: 0,
                        nov: 0,
                        dec: 0,
                        jan: 0,
                        feb: 0,
                        mar: 0,
                        record_ids: [] // To store record ids
                    };
                }
                aggregatedData[key].apr += record.apr;
                aggregatedData[key].may += record.may;
                aggregatedData[key].jun += record.jun;
                aggregatedData[key].jul += record.jul;
                aggregatedData[key].aug += record.aug;
                aggregatedData[key].sep += record.sep;
                aggregatedData[key].oct += record.oct;
                aggregatedData[key].nov += record.nov;
                aggregatedData[key].dec += record.dec;
                aggregatedData[key].jan += record.jan;
                aggregatedData[key].feb += record.feb;
                aggregatedData[key].mar += record.mar;
                aggregatedData[key].record_ids.push(record.id); // Store record id
            });
            return Object.values(aggregatedData);
        },
        
        _renderRows: function(aggregatedData) {
            var $tbody = this.$('#forecasted_release_report_tbody');
            $tbody.empty();
            
            aggregatedData.forEach(function(record) {
                var $row = $(QWeb.render('ForecastedReleaseReportRow', { record: record }));
                $row.data('record-ids', record.record_ids);
                $row.find('td[data-month]').each(function() {
                    var $cell = $(this);
                    if ($cell.text().trim() !== '0') {
                        $cell.addClass('clickable');
                    }
                });
                $tbody.append($row);
            });
        },
        
        _onCellClick: function(event) {
            var $cell = $(event.currentTarget);
            var month = $cell.data('month');
            var record_ids = $cell.closest('tr').data('record-ids');
            
            var domain = [['id', 'in', record_ids], [month, '>', 0]];
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'forecasted_release_report',
                view_mode: 'tree',
                views: [[false, 'list']],
                domain: domain,
                target: 'new',
            });
        },
    });
    
    core.action_registry.add('forecasted_release_report_client_tag', ForecastedReleaseReport);
    
    return ForecastedReleaseReport;
});
