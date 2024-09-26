odoo.define('kw_onboarding.kwonboard_education_validation', function (require) { 
    'use strict';
   // $.validator.setDefaults({ ignore: '' });
    var edu = {
        prof_current_id: 0,
        cert_current_id: 0,
        prof_clone: '',
        cert_clone: '',
        init: function(){
            this.prof_current_id = $('#professional_qualification_block').find('tr').size();
            this.cert_current_id = $('#training_certification_block').find('tr').size();
            this.prof_clone = $('#professional_qualification_block').find('tr').eq(0).clone();
            this.cert_clone = $('#training_certification_block').find('tr').eq(0).clone();
            //Professional Courses add more
            this.showHideBtn();
            this.bindEvent('');
            this.validateForm();
            this.select2();

            //Start : grade and percentage validation after key up..
            $(document).on("keydown keyup", "input[type=text]", function(){
                var re = /^((0|[1-9]\d?)(\.\d{1,2})?|100(\.00?)?)$/;
                //re.test("95")
                var $el = $(this);
                var val = $.trim( $el.val() ) || "";
                //Grade
                if ($el.hasClass("gradeval")) {
                    val = val.replace(/[^a-z0-9\s]/gi, '');
                }
                $el.val(val);
                //Percentage
                if ($el.hasClass("percentval")){
                    if (val < 0) val = 0;
                    //if (val > 100) val = 100;
                    if (val.length < 3){
                        val = val.replace(/[^0-9]/gi, '');
                    } else if (val.length > 3){
                        if (!(/^[0-9]+$/i.test(val[val.length-1]))){
                            val = val.slice(0,3);
                        }
                    }
                    if (val==0) {
                        val = '';
                    } else if (val.length==2) {
                        val=val.concat(".");
                        //val = (val / 100).toFixed(2);
                    } else if (val.length>5) {
                        val=val.substr(0,5);
                    }
                }
                $el.val(val);
            });
        //End : grade and percentage validation after key up..
        },
        addMore: function(mode){
            var current_id = mode == 'prof' ? this.prof_current_id++ : this.cert_current_id++;
            var newElement = mode == 'prof' ? this.prof_clone.clone() : this.cert_clone.clone();
            newElement.find("input").val("");
            newElement.find('select').val('');
            newElement.find(".txt-filename").text("");
            newElement.find('select,input').each(function(){
                $(this).attr('id',$(this).attr('id').replace(/\d+/,current_id));
                $(this).attr('name',$(this).attr('name').replace(/\d+/,current_id));
            });
            newElement.find('span').each(function(){
                $(this).attr('id',$(this).attr('id').replace(/\d+/,current_id));
            });

            if(mode == 'prof'){
                $('.remove_prof:last').show();
                $("#professional_qualification_block").append(newElement);
            } else {
                $('.btn_hide_cert:last').show();
                $("#training_certification_block").append(newElement);
            }
            //this.bindEvent('clone', newElement);
            this.showHideBtn();
            this.select2();
            //$('select').select2();
        },
        showHideBtn: function(mode){
            return true;
            $('.btn_add_prof').not(':last').hide();
            $('.btn_remove_prof').not(':last').show();
            $('.btn_remove_prof:last').hide();
            $('.btn_add_cert').not(':last').hide();
            $('.btn_hide_cert').not(':last').show();
            $('.btn_hide_cert:last').hide();
        },
        removeRow: function(el, mode){
            $(el).closest('tr').remove();
        },
        bindEvent: function(mode, el){
            $(document)
            .on('click', '.btn_add_prof', function(){
                edu.addMore('prof');
            })
            .on('click', ".btn_remove_prof", function(){
                edu.removeRow(this,'prof');
            })
            .on('click', '.btn_add_cert', function(){
                edu.addMore('cert');
            })
            .on('click', ".btn_hide_cert", function(){
                edu.removeRow(this,'cert');
            })
            .on('change', ".clsfrmfile", function(){
                var _el         = $(this);
                var filename    = _el.val();
                var $file       = _el.closest('td').find(".file-upload");
                var $noFile     = _el.closest('td').find(".file-select-name");
                var ddlFileName = _el.closest('td').find(".txt-filename");
                var ddlHdnFileName = _el.closest('td').find('input[type=hidden]')
            
                if (/^\s*$/.test(filename)) {
                    $file.removeClass('active');
                    $noFile.text("No file chosen...");
                    ddlFileName.html("");
                    ddlHdnFileName.val('');
                } else {
                    $file.addClass('active');
                    $noFile.text(filename.replace("C:\\fakepath\\", ""));
                    ddlFileName.html(filename.replace("C:\\fakepath\\", ""));
                    ddlHdnFileName.val(filename.replace("C:\\fakepath\\", ""));
                }
            })
            .on('change',".clseducationstream", function(){
                var _el       = $(this);
                var stram_id  = _el.val();
                var data_section = _el.closest('tr').find(".clsSpecializationdata")
                var ajax = require('web.ajax');
                ajax.jsonRpc("/getStreamwisespecialization", 'call', {'stream_id' :stram_id})
                    .then(function (values) {
                        data_section.empty();
                        var html_content = ''
                        if (values !="None"){
                            $.each( values, function( key, value ) {                                
                                html_content+='<div class="checkbox">'
                                html_content+='    <label>'
                                html_content+='        <input value="'+value['id']+'" type="checkbox" id="specialization_'+stram_id+'_'+value['id']+'" name="specialization_'+stram_id+'_'+value['id']+'" />'
                                html_content+= value['name']+'</label>'
                                html_content+='</div>'
                            });
                            data_section.append(html_content);
                        }
                });
            });
        },
        validateForm: function(){
            $.validator.messages.accept     = 'File must be .jpeg,.png, .pdf format';
            $.validator.messages.filesize   = 'File size must be less than 4 MB';
            $.validator.addClassRules({
                clsrequired_1: {
                    required    : true,
                },
                clsfrmfile: {
                    required    : function(element) {
                            var hdnfile = $(element).closest('td').find('input[type=hidden]')
                            var otherelms = $(element).closest('tr').find('.likert-field')
                            var blankfield = 0;

                            $(element).closest('tr').find('.likert-field').each(function(){
                                if($(this).val()!='')
                                    blankfield++
                            });
                            return $(hdnfile).val()=='' && ($(hdnfile).hasClass('clsrequired_1') || blankfield>0);
                      },
                    accept      : "image/png,image/jpeg,image/jpg,application/pdf",
                    filesize    : 4194304
                },                 
            });

            // configure your validation
            $("form#frm_onboard_education").submit(function(e) {
                e.preventDefault();
            }).validate({
                // Make sure the form is submitted to the destination defined
                // in the "action" attribute of the form when valid
                submitHandler: function (frm) {
                    frm.submit();
                },
                errorElement: "div",
                highlight: function (element) {
                    $(element).css('background', '#ffdddd');
                },
                // Called when the element is valid:
                unhighlight: function (element) {
                    $(element).css('background', '#ffffff');
                },
                // success: "valid"

            });//End of validate()
            // $('#tbledu tr:lt(3) input[type !="file"],#tbledu tr:lt(3) select').each(function(){
            //     if ($(this).val()==""){
            //         $(this).rules('add',{
            //             required: true,
            //             messages: {
            //                 required:$(this).attr('placeholder')+" is required.",
            //             }
            //         });
            //     }
            // });
        },
        select2: function(){
            $('select').select2();
            $('[data-rel="tooltip"]').tooltip();
        }
    };

    $(function(){
        edu.init();
    }); //end of ready function

}); // End of module
