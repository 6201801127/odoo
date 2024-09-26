odoo.define('hr_applicant.kanban_renderer',function(require){
    "use strict";
    
    
    var KanbanRenderer = require('web.KanbanRenderer');
    
    KanbanRenderer.include({
    
        _setState: function (state) {
            this._super.apply(this, arguments);
    
            var arch = this.arch;
            var drag_drop = true;
            if (arch.attrs.disable_drag_drop_record) {
                if (arch.attrs.disable_drag_drop_record=='true') {
                    this.columnOptions.draggable = false;
                }
            }
    
        },    
    
    });
    
    });