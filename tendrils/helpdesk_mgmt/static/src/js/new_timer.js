odoo.define('helpdesk_mgmt.new_timer', function (require) {
    "use strict";
        var AbstractField = require('web.AbstractField');
        var core = require('web.core');
        var field_registry = require('web.field_registry');
        var time = require('web.time');
        var FieldManagerMixin = require('web.FieldManagerMixin');
        
        var _t = core._t;
        
        var TimeCounterNew  = AbstractField.extend({
            
            init: function() {
                this._super.apply(this, arguments);
                this.duration = 1000;
                this.state = 'new';
            },
            willStart: function () {
                var self = this;
                var def = this._rpc({
                    model: 'helpdesk.ticket',
                    method: 'get_timer_state_new',
                    args : [self.res_id]
                }).then(function (result) {
                    self.state = result[0];
                    self.duration = result[1];
                });
                return $.when(this._super.apply(this, arguments), def);
            },
            
            destroy: function () {
                this._super.apply(this, arguments);
                clearTimeout(this.timer);
            },
            isSet: function () {
                return true;
            },
           
        
            _render: function () {
                this._startTimeCounter();
            },
            _startTimeCounter: function () {
                var self = this;
                var create_datetime = moment(this.recordData.last_stage_update);
                var time_gap = moment.duration(moment().diff(create_datetime));
                clearTimeout(this.timer);
                
                if (this.state == 'New') {
                    this.timer = setTimeout(function () {
                        self.duration = time_gap + 1000;
                        self._startTimeCounter();
                        self._rpc({
                            model: 'helpdesk.ticket',
                            method: 'save_new_timer_time',
                            args : [[self.res_id,self.duration]]
                        }).then(function (result) {
                            
                        });
                    }, 1000);
               } else {
                    console.log('taken time')
                }
                this.$el.html($('<span>' + moment.utc(self.duration).format("HH:mm:ss") + '</span>'));
            },
        });
        field_registry.add('newcountdown', TimeCounterNew);
    
    });
    