odoo.define('kw_employee_covid_data_js.covid', function (require) { 
    'use strict';
    
    //---- Custom Scripts for captcha verification
    $(document).ready(function(){
        let selectedDose = $("input[type='radio']:checked").val();;
        let dateError = false;
        let dueDateError = false;
        let doc1Error = false;
        let doc2Error = false;
        let remarkError = false;
        
        $('#covid_data_form').submit(function(){
            checkExtension('#document2','#doc2_error');
            checkExtension('#document1','#doc1_error');

            console.log(selectedDose)
            if (selectedDose === 'first_dose') {
                if(!$('#due_date').val()){
                    $('#due_date_error').show();
                    dueDateError = true;
                    return false;
                }
                else if(!doc1Error){
                    $('#doc1_error').show();
                    return false;
                }
            }
            if (selectedDose === 'second_dose') {
                if(!$('#date').val()){
                    $('#date_error').show();
                    dateError = true;
                    return false;
                }
                else if(!doc2Error){
                    $('#doc2_error').show();
                    checkExtension('#document2','#doc2_error');
                    return false;
                }
            }
            if (selectedDose === 'no_dose_taken') {
                if(!$('#remark').val()){
                    $('#remark_error').show();
                    remarkError = true;
                    return false;
                }
                else{
                    $('#remark_error').hide();
                }
            }
            return true;
        })

        // Dynamically Alter fields According to radio button selected
        $("input[type='radio']").click(() => {
            let radioButtonVal = checkRadioVal();
            selectedDose = radioButtonVal;
            if (radioButtonVal === 'first_dose') {
                $('#due_date_field,#dose1_field').each(function(){
                    $(this).show();
                })
                $('#remark_field,#dose2_field,#date_field,#date_error,#doc2_error,#remark_error').each(function(){
                    $(this).find('input').val('');
                    $(this).hide();
                })
            }
            if (radioButtonVal === 'second_dose') {
                $('#date_field,#dose2_field').each(function(){
                    $(this).show();
                })
                $('#remark_field,#dose1_field,#due_date_field,#due_date_error,#doc1_error,#remark_error').each(function(){
                    $(this).find('input').val('');
                    $(this).hide();
                })
            }
            if (radioButtonVal === 'no_dose_taken') {
                $('#date_field,#due_date_field,#dose1_field,#dose2_field,#due_date_error,#doc1_error,#date_error,#doc2_error').each(function(){
                    $(this).find('input').val('');
                    $(this).hide();
                })
                $('#remark_field').show();
            }
        })

        //Function to get Selected Radio Button Value
        function checkRadioVal(){
            let radioVal = $("input[type='radio']:checked").val();
            return radioVal;
        }
        $('#document1').change(function () {
            doc1Error = checkExtension('#document1','#doc1_error');
        });
    
        $('#document2').change(function () {
            doc2Error = checkExtension('#document2','#doc2_error');
        });
    
        function checkExtension(id,error_id) { 
            let element = $(id).val();
            let elementExtension = element.split('.').pop();
            const extensions = ["pdf"]
            console.log(element.length);
            if (element.length == 0){
                $(error_id).show();
                $(error_id).html("Document is Required!");
                return false;
            }
            else {
                $(error_id).hide();
                if(extensions.includes(elementExtension.toLowerCase())!=true){
                    $(error_id).show();
                    $(error_id).html("*.pdf File Only Supported!");
                    return false;
                }
                else{
                    $(error_id).hide();
                    return true;
                }
            }
           
        }
    });


});