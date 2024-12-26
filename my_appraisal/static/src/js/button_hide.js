odoo.define('my_appraisal.button_hide', function (require) {
    "use strict";
  
    var FormController = require('web.FormController');
  
    FormController.include({
        updateButtons: function () {
            if (!this.$buttons) {
                return;
            }
            if (this.footerToButtons) {
                var $footer = this.renderer.$el && this.renderer.$('footer');
                if ($footer && $footer.length) {
                    this.$buttons.empty().append($footer);
                }
            }
            
            if (this.modelName === "employee.appraisal") {  
          
                if (this.renderer.state.data.state == "completed" || this.renderer.state.data.state == "rejected") {
                    this.$buttons.find('.o_form_button_edit')
                            .toggleClass('o_hidden', true);
                } else {
                    this.$buttons.find('.o_form_button_edit')
                            .toggleClass('o_hidden', false);
                }

                if (this.renderer.state.data.state == "self_review" && this.renderer.state.data.ra_group_bool_check != true) {
                    this.$buttons.find('.o_form_button_edit')
                            .toggleClass('o_hidden', true);
                } 

                if (this.renderer.state.data.state == "reporting_authority_review" && this.renderer.state.data.review_group_bool_check != true) {
                    this.$buttons.find('.o_form_button_edit')
                            .toggleClass('o_hidden', true);
                } 
                if (this.renderer.state.data.state == "reviewing_authority_review" && this.renderer.state.data.manager_group_bool_check != true) {
                    this.$buttons.find('.o_form_button_edit')
                            .toggleClass('o_hidden', true);
                } 
               
            } else {
                this.$buttons.find('.o_form_button_edit')
                        .toggleClass('o_hidden', false);
              }
            var edit_mode = (this.mode === 'edit');
            this.$buttons.find('.o_form_buttons_edit')
                .toggleClass('o_hidden', !edit_mode);
            this.$buttons.find('.o_form_buttons_view')
                .toggleClass('o_hidden', edit_mode);
  
        }
      
      });
    });