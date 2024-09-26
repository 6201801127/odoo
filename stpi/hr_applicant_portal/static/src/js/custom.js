
$(document).ready(function(){

    $('#dob').on('change', function(){
        var dateString = $(this).val();
        var myDate = new Date(dateString);
        var today = new Date();
        if ( myDate > today ) { 
            alert("You cannot enter a date in the future!");
            $('#dob')[0].value = '';
            return false;
        }
        return true;
    });

    $('.is_applicable_fee').on('change', function(){
        var is_applicable_fee = $(this).val();
        if (is_applicable_fee == 'No'){
            $('#applicable_fee')[0].style.display = "none";
        }
        else{
            $('#applicable_fee')[0].style.display = "block";
        }
    });

    $('.category_id').on('change', function(){
        $.ajax({
            url: '/getAdvertisementName',
            type: 'GET',
            data : {'category_ids': $(this).val()},
            beforeSend : function() {
//                    $("#loader").css('display', 'block');
                $(".custom_preloader").css("display", "block");
            },
            complete : function() {
//                    $("#loader").css("display", "none");
                $(".custom_preloader").css("display", "none");
            },
            success: function(response){
                if (response != undefined){
                    var response_data = JSON.parse(response)['result'];
                    $(".advertisement_line_id").empty();
                    var html_content = "<option value=''>Select</option>";
                    for(var i=0;i<response_data.length;i++){
                        html_content += "<option id='advertisement_id' name='advertisement.id' value='"+response_data[i][0]+"'>"+response_data[i][1]+"</option>";
                    }
                    $(".advertisement_line_id").append(html_content);
                }
                else{
                    $("option").remove("#advertisement_id");
                    $(".advertisement_line_id").append("<option value=''/>");
                }

            },
            error: function(response) {
                alert('Error : '+response);
            }
        });
    });

    $('.advertisement_line_id').on('change', function(){
        $.ajax({
            url: '/getJobName',
            type: 'GET',
            data : {'advertisement_ids': $(this).val()},
            beforeSend : function() {
//                    $("#loader").css('display', 'block');
                $(".custom_preloader").css("display", "block");
            },
            complete : function() {
//                    $("#loader").css("display", "none");
                $(".custom_preloader").css("display", "none");
            },
            success: function(response){
                if (response != undefined){
                    var response_data = JSON.parse(response)['result'];
                    $(".job_id").empty();
                    var html_content = "<option value=''>Select</option>";
                    for(var i=0;i<response_data.length;i++){
                        html_content += "<option id='course_id' name='courses.id' value='"+response_data[i][0]+"'>"+response_data[i][1]+"</option>";
                    }
                    $(".job_id").append(html_content);
                }
                else{
                    $("option").remove("#course_id");
                    $(".job_id").append("<option value=''/>");
                }

            },
            error: function(response) {
                alert('Error : '+response);
            }
        });
    });
});