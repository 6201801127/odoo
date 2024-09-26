odoo.define('kw_emp_profile.emp_profile_view', function (require) {
    "use strict";

    $(function(){

        var FormController = require('web.FormController');
        var ExtendFormController = FormController.include({
            saveRecord: function () {
                var res = this._super.apply(this, arguments);
                if(this.modelName == 'kw_emp_profile'){
                    resize_percentage();
                    // var self = this;
                    // res.then(function(changedFields){
                    //     console.log(changedFields);
                    //     self.do_notify('title', 'message');
                    // });
                }
                return res;
            },
            discardChanges: function () {
                var res = this._super.apply(this, arguments);
                if(this.modelName == 'kw_emp_profile'){
                    resize_percentage();
                }
                return res;
            },
            _updateButtons: function () {
                var res = this._super.apply(this, arguments);
                if(this.modelName == 'kw_emp_profile'){
                    resize_percentage();
                }
                return res;
            },
            update: function () {
                var res = this._super.apply(this, arguments);
                if(this.modelName == 'kw_emp_profile'){
                    resize_percentage();
                }
                return res;
            },
        });
        $( window ).resize(function() {
            resize_percentage();
        });
        setTimeout(function(){
            resize_percentage();
        }, 1500)
        var resize_percentage = function(){

            $('.notebook_emp_profile').find('.nav-item').each(function(k,i){
                var _el = $(this);
                $('.emp_profile_percentage_block').find('h2:eq('+k+')').width(_el.width());
            });
        }


    });
});