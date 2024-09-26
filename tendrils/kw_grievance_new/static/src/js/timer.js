// odoo.define('kw_grievance_new.timer', function (require) {
//     "use strict";
//         var AbstractField = require('web.AbstractField');
//         var core = require('web.core');
//         var field_registry = require('web.field_registry');
//         var time = require('web.time');
//         var FieldManagerMixin = require('web.FieldManagerMixin');
        
//         var _t = core._t;
        
//         var TimeCounter  = AbstractField.extend({
            
//             init: function() {
//                 this._super.apply(this, arguments);
//                 this.duration = 1000;
//                 this.state = 'new';
//             },
//             willStart: function () {
//                 var self = this;
//                 var def = this._rpc({
//                     model: 'grievance.ticket',
//                     method: 'get_timer_state',
//                     args : [self.res_id]
//                 }).then(function (result) {
//                     self.state = result[0];
//                     self.duration = result[1];
//                 });
//                 return $.when(this._super.apply(this, arguments), def);
//             },
            
//             destroy: function () {
//                 this._super.apply(this, arguments);
//                 clearTimeout(this.timer);
//             },
//             isSet: function () {
//                 return true;
//             },
            
            
//             _render: function () {
//                 console.log("duration",this.recordData.duration)
//                 this.resolution_duration = this.recordData.duration;
//                 this._startTimeCounter();
//             },
//             _startTimeCounter: function () {
//                 var self = this;
//                 var create_datetime = moment(this.recordData.last_stage_update);
                
//                 var time_gap = moment.duration(moment().diff(create_datetime));
//                 clearTimeout(this.timer);
                
//                 if (this.state == 'In Progress') {
//                     this.timer = setTimeout(function () {
//                         // console.log(self.duration,this.resolution_duration, time_gap)
//                         if (self.resolution_duration > 0){
//                             self.duration = self.resolution_duration + 1000;
//                             self.resolution_duration += 1000;
//                         } 
//                         else{
//                             self.duration = time_gap + 1000;
//                         }
//                         self._startTimeCounter();
//                         self._rpc({
//                             model: 'grievance.ticket',
//                             method: 'save_timer_time',
//                             args : [[self.res_id,self.duration]]
//                         }).then(function (result) {
                            
//                         });
//                     }, 1000);
//                 } else {
//                     // console.log('taken time')
//                 }
//                 this.$el.html($('<span>' + moment.utc(self.duration).format("HH:mm:ss") + '</span>'));
//             },
//         });
//         field_registry.add('countdown', TimeCounter);
    
//     });
    