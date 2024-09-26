odoo.define('kw_synchronization.ListController', function (require) {
    "use strict";
    
    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if(this.modelName == 'res.country' && this.viewType == 'list'){
                this.user_group();
                this.button_click();
            }
            if(this.modelName == 'hr.employee' && this.viewType == 'list'){
                this.button_click_emp();
                this.employee_group();
            }
            if(this.modelName == 'kw_location_master' && this.viewType == 'list'){
                this.button_click_location();
                this.location_group();
            }
            // -------Designation function start-----
            if(this.modelName == 'hr.job' && this.viewType == 'list'){
                this.button_designation_sync();
                this.check_designation_group();
            }
            // -------Designation function end-----

            // -------Technical Skill Category Master function start-----
            if(this.modelName == 'kwemp_technical_category' && this.viewType == 'list'){
                this.button_skill_cat_master_sync();
                this.check_skill_cat_master_group();
            }
            // -------Technical Skill Category Master function end-----

            // -------Technical Skill function start-----
            if(this.modelName == 'kwemp_technical_skill' && this.viewType == 'list'){
                this.button_skill_sync();
                this.check_skill_group();
            }
            // -------Technical Skill function end-----

            // -------Grade function start-----
            if(this.modelName == 'kwemp_grade' && this.viewType == 'list'){
                this.button_grade_sync();
                this.fun_check_grade_group();
            }
            // -------Grade function end-----

            // -------Employeement Type function start-----
            if(this.modelName == 'kwemp_employment_type' && this.viewType == 'list'){
                this.button_emp_type_sync();
                this.fun_check_emp_type_group();
            }
            // -------Employeement Type function end-----

            // -------Stream function start-----
            if(this.modelName == 'kwmaster_stream_name' && this.viewType == 'list'){
                this.button_stream_sync();
                this.fun_check_stream_group();
            }
            // -------Stream function end-----

            // -------Specialization function start-----
            if(this.modelName == 'kwmaster_specializations' && this.viewType == 'list'){
                this.button_specialization_sync();
                this.fun_check_specialization_group();
            }
            // -------Specialization function end-----

            // -------Category function start-----
            if(this.modelName == 'kwmaster_category_name' && this.viewType == 'list'){
                this.button_category_sync();
                this.fun_check_category_group();
            }
            // -------Category function end-----

            // -------Branch function start-----
            // if(this.modelName == 'kw_res_branch' && this.viewType == 'list'){
            //     this.button_branch_sync();
            //     // this.fun_check_branch_group();
            // }
            // -------Branch function end-----

            // -------Language function start-----
            if(this.modelName == 'kwemp_language_master' && this.viewType == 'list'){
                this.button_language_sync();
                this.fun_check_language_group();
            }
            // -------Language function end-----
           
        },

    // ======= Language Master Group Check Start=========
        fun_check_language_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwemp_language_master',
                    method: 'check_language_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_language_button').hide();
                    }
                });
        },
    // ======= Language Master Group Check End=========

    // ======= Language Master Sync Start ========
        button_language_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_language_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Language Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwemp_language_master',
                            method: 'action_sync_language',
        
                        })
                     
                    }
                  }
                );
                
                // self._rpc({
                //     model: 'kwemp_language_master',
                //     method: 'action_sync_language',
                // })
            });
        },
    //  ====== Language Master Sync End ========

    // ======= Branch Master Group Check Start=========
        // fun_check_branch_group: function(){
        //     var self = this;
        //     var user = session.uid;
        //     return rpc.query({
        //             model: 'kw_res_branch',
        //             method: 'check_branch_group',
        //         }).then(function (value) {
        //             if(value != '1'){
        //                 self.$buttons.find('.oe_action_sync_branch_button').hide();
        //             }
        //         });
        // },
    // ======= Branch Master Group Check End=========

    // ======= Branch Master sync Start=========
        // button_branch_sync: function(){
        //     var self = this;
        //     this.$buttons.on('click', '.oe_action_sync_branch_button', function () {
        //         swal({
        //             title: "Are You Sure?",
        //             text: "You are going to Sync Branch Data to Tendrils",
        //             type: "warning",
        //             confirmButtonColor: "#108fbb",
        //             showCancelButton: true,
        //             confirmButtonText: "Sync Data",
        //             cancelButtonText: "No",
        //           },
        //           function(isConfirm){
        //             if (isConfirm) {
        //                 self._rpc({

        //                     model: 'kw_res_branch',
        //                     method: 'action_sync_branch',
        
        //                 })
                     
        //             }
        //           }
        //         );
        //         // self._rpc({
        //         //     model: 'kw_res_branch',
        //         //     method: 'action_sync_branch',
        //         // })
        //     });
        // },
    // ======= Branch Master sync End=========

    // ======= Category Master Group Check Start=========
        fun_check_category_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwmaster_category_name',
                    method: 'check_category_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_category_button').hide();
                    }
                });
        },
    // ======= Category Master Group Check End=========

    // ======= Employee Category Master Sync Start ========
        button_category_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_category_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Employee Category Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwmaster_category_name',
                            method: 'action_sync_emp_category',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({
                //     model: 'kwmaster_category_name',
                //     method: 'action_sync_emp_category',
                // })
            });
        },
    //  ====== Employee Category Master Sync End ========

    // ======= Specialization Master Group Check Start=========
        fun_check_specialization_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwmaster_specializations',
                    method: 'check_specialization_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_specialization_button').hide();
                    }
                });
        },
    // ======= Specialization Master Group Check End=========    

    // ======= Specialization Master Sync Start ========
        button_specialization_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_specialization_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Specialization Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwmaster_specializations',
                            method: 'action_sync_specialization',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({
                //     model: 'kwmaster_specializations',
                //     method: 'action_sync_specialization',
                // })
            });
        },
    //  ====== Specialization Master Sync End ========

    // ======= Stream Master Group Check Start=========
        fun_check_stream_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwmaster_stream_name',
                    method: 'check_stream_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_stream_button').hide();
                    }
                });
        },
    // ======= Stream Master Group Check End=========    
        
    // ======= Employeement Type Master Group Check Start=========
        fun_check_emp_type_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwemp_employment_type',
                    method: 'check_employeement_type_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_emp_type_button').hide();
                    }
                });
        },
    // ======= Employeement Type Master Group Check End=========

    // ======= Employeement Type Master Sync Start ========
        button_emp_type_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_emp_type_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Employment type Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwemp_employment_type',
                            method: 'action_sync_emp_type',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({
                //     model: 'kwemp_employment_type',
                //     method: 'action_sync_emp_type',
                // })
            });
        },
    //  ====== Employeement Type Master Sync End ========

    // ======= Stream Master Sync Start ========
        button_stream_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_stream_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Stream Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwmaster_stream_name',
                            method: 'button_stream_sync',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({
                //     model: 'kwmaster_stream_name',
                //     method: 'button_stream_sync',
                // })
            });
        },
//  ====== Stream Master Sync End ========
        
        location_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kw_location_master',
                    method: 'check_location_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_location_button').hide();
                    }
                });
        },
        button_click: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_country_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Country Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'res.country',
                            method: 'action_sync_country',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'res.country',
                //     method: 'action_sync_country',

                // })
            });
        },
        button_click_location: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_location_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Location Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kw_location_master',
                            method: 'action_sync_location',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'kw_location_master',
                //     method: 'action_sync_location',

                // })
            });
        },
        button_click_emp: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_employee_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Employee Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'hr.employee',
                            method: 'action_sync_employee',
        
                        })
                     
                    }
                  }
                );
            });
        },
        // --------Grade Sync Button--------
        button_grade_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_grade_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Grade Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwemp_grade',
                            method: 'action_sync_grade',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'kwemp_grade',
                //     method: 'action_sync_grade',

                // })
            });
        },
        // -------Grade sync end--------

        // --------Designation Sync Button--------
        button_designation_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_designation_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Designation Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'hr.job',
                            method: 'action_sync_designation',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'hr.job',
                //     method: 'action_sync_designation',

                // })
            });
        },
        // -------Designation sync end--------

        // --------Skill Master Sync Button--------
        button_skill_cat_master_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_tech_skill_category_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Technical Category Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwemp_technical_category',
                            method: 'action_sync_skill',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'kwemp_technical_category',
                //     method: 'action_sync_skill',

                // })
            });
        },
        // -------Skill Master sync end--------

        // --------Skill Master Sync Button--------
        button_skill_sync: function(){
            var self = this;
            this.$buttons.on('click', '.oe_action_sync_tech_skill_button', function () {
                swal({
                    title: "Are You Sure?",
                    text: "You are going to Sync Technical Skill Data to Tendrils",
                    type: "warning",
                    confirmButtonColor: "#108fbb",
                    showCancelButton: true,
                    confirmButtonText: "Sync Data",
                    cancelButtonText: "No",
                  },
                  function(isConfirm){
                    if (isConfirm) {
                        self._rpc({

                            model: 'kwemp_technical_skill',
                            method: 'action_sync_skill_master',
        
                        })
                     
                    }
                  }
                );
                // self._rpc({

                //     model: 'kwemp_technical_skill',
                //     method: 'action_sync_skill_master',

                // })
            });
        },
        // -------Skill Master sync end--------

        user_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'res.country',
                    method: 'check_sync_country',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_country_button').hide();
                    }
                });
        },
        employee_group: function(){
            var self = this;
            let params = (new URL(document.location)).searchParams;
            var new_url = document.URL
            var list = new_url.split("=")
            console.log("list====",list[list.length-1])
            var menu_id = list[list.length-1]
            
            return rpc.query({
                    model: 'hr.employee',
                    method: 'check_employee_group',
                    args:[{'menu_id': menu_id}]
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_employee_button').hide();
                    }
                });
        },

        // ------Group check for Grade Start------
        fun_check_grade_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwemp_grade',
                    method: 'check_grade_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_grade_button').hide();
                    }
                });
        },
        // ------Group check for Grade End------


        // ------Group check for Designation Start------
        check_designation_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'hr.job',
                    method: 'check_designation_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_designation_button').hide();
                    }
                });
        },
        // ------Group check for Designation End------

        // ------Group check for skill category master Start------
        check_skill_cat_master_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwemp_technical_category',
                    method: 'check_sync_skill_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_tech_skill_category_button').hide();
                    }
                });
        },
        // ------Group check for skill category master End------

        // ------Group check for skill master Start------
        check_skill_group: function(){
            var self = this;
            var user = session.uid;
            return rpc.query({
                    model: 'kwemp_technical_skill',
                    method: 'check_sync_skill_master_group',
                }).then(function (value) {
                    if(value != '1'){
                        self.$buttons.find('.oe_action_sync_tech_skill_button').hide();
                    }
                });
        }
        // ------Group check for skill master End------
    
    });
    
    return ListController;
    
    });
    