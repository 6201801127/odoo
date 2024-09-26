odoo.define('kw_recruitment_consultancy.common', function (require) {
	'use strict';
	
	var session = require('web.session');
	var ajax = require('web.ajax');
	
	
	function jsonp(action, data) {
		$.blockUI();
		ajax.jsonRpc(action, 'call', data)
        .then(function (response) {
			$("div.blockUI").remove();
        	if (response['message_type'] == 'f'){
        		swal("OOPS!", response['message'], "error");
        	}
        	if (response['message_type'] == 's'){
				$("#verifyCaptcha").attr("disabled", true);
        		swal({
        			title: response['message'],
        			text: "",
        			content: response['message'],
        			dangerMode: true,
        			buttons: {
        				confirm: { text: 'ok', className: 'btn-success' }
        			},
        		})
        			.then(function (isConfirm) {
        				if (isConfirm) {
        					window.location.href = window.location.origin + response['url'];
        				} 
        		});
        		
        	}
           
        });
	}

	
	//---- Custom Scripts
	$(document).ready(function () {

		$('#vc').on('change', function () {
			if (this.value == 'other') {
				$('#other_url').show();
				$("#other_url_input").prop('required', true);
			} else {
				$("#other_url_input").prop('required', false);
				$('#other_url').css('display', 'none')
			}
		});
		$(".div_location").css('display', 'none');
		$(".div_room").css('display', 'none');
		if($('#applicant').val()!='null'){
			$('#applicant_error').hide();
		}
		$('#error_panel').hide();
		$('#error_room').hide();

		if($('#moi').val()=='face2face'){
			$('.div_location').css('display', 'block');
			$(".div_room").css('display', 'block');
		}

		if($('#moi').val()=='telephonic'){
			$(".div_phone").css('display','block');
			if ($('#ph_number').val()){
				$('#ph_error_message').hide();
			}
			if($('#location').val()){
				$('.div_location').css('display', 'block');
				$(".div_room").css('display', 'block');
			}
			else{
				$('.div_location').css('display', 'none');
				$(".div_room").css('display', 'none');
			}
		}
		$('#location').on('change', function(){
			if(($('#location').val()=='') && ($('#moi').val()=='telephonic')){
				$('#error_loc').hide();	
				$('#error_room').hide();
			}
			if(($('#location').val()=="") && ($('#moi').val()=='teamviewer')) {
				$('#error_loc').hide();	
				$('#error_room').hide();
			}
		})

		//// set req for location & meeting room
		$('#moi').on('change', function() {
			if(this.value =='face2face'){
				$(".div_phone").css('display','none');
				$("#location").prop('required',true);
				$("#meeting_room").prop('required',true);
				$(".div_location").css('display', 'block');
				$('#error_loc').hide();	
				$(".div_room").css('display', 'block');
				$('#error_url').hide();
			}
			else if (this.value == 'telephonic') {
				$("#ph_number").prop('required', true);
				$("#ph_number").val('');
				$('#ph_error_message').hide();
				$('#ph_number').keyup(function () {					//  meeting form validation-- ph number
					checkMobile('#ph_number','#ph_error_message');
				});
				$(".div_phone").css('display', 'block');
				$(".div_location").css('display', 'block');
				$(".div_room").css('display', 'block');
				$('#error_loc').hide();	
				$('#error_room').hide();
				$('#error_url').hide();

			}
			else {
				$("#location").prop('required', false);
				$("#meeting_room").prop('required', false);
				$("#ph_number").prop('required', false);
				$(".div_phone").css('display', 'none');
				$(".div_location").css('display', 'block');
				$(".div_room").css('display', 'block');
				$('#error_loc').hide();
				$('#ph_error_message').hide();
				$('#error_url').hide();
				$('#error_room').hide();
				$('#error_url').hide();
			}
		});


		//For add applicant required field and message
		$('#FormControlSelectQuali').on('change', function () {
			if (this.value == 1) {
				$('#txtQualification').show()
				$("#cQualificationT").prop('required', true);
				$('#verifyCaptcha').click(function () {
					if ($("#cQualificationT").val() === '') {
						$('#required_message').html('Other Qualification is required.')
					}
				})
			} else {
				$('#txtQualification').css('display', 'none')
			}
		});

		$('#EditFormControlSelectQuali').on('change', function () {
			console.log($('#EditFormControlSelectQuali').val())
			if (this.value == 'Others') {
				$('#OtheQualification').show();
				$("#otherQualificationT").prop('required', true);
			} else {
				$('#OtheQualification').css('display', 'none');
			}
		});

	

		$('#meeting_title').on('change', function () {
			$('#agenda').val(this.value);
			$('#agenda').parents('.control-group').addClass('focused');
		});

		$('#participant_details').on('change', function () {
			var selected = [];
			for (var option of document.getElementById('participant_details').options) {
				if (option.selected) {
					selected.push(option.value);
				}
			}
			$('#employee_id').val(selected);
			checkSelect('#participant_details','#error_panel');
		});

		$('#applicant').on('change', function () {
			var selected = [];
			for (var option of document.getElementById('applicant').options) {
				if (option.selected) {
					selected.push(option.value);
				}
			}
			$('#applicant_id').val(selected);
		});
		
		$('#FormControlSelectSkill').on('change', function() {
			var selected = [];
		    for (var option of document.getElementById('FormControlSelectSkill').options)
		    {
		        if (option.selected) {
		            selected.push(option.value);
		        }
		    }
			$('#skill_id').val(selected);
		});

		$('#SelectTechSkills').on('change', function () {
			console.log('tech skill called')
			var selected = [];
			for (var option of document.getElementById('SelectTechSkills').options) {
				if (option.selected) {
					selected.push(option.value);
				}
			}
			$('#skill_id').val(selected);
			checkSelect('#skill_id','#tech_skill_message');
		});

		
		$( ".form-control" )
	    .on('focus',function() {
	       $(this).parents('.control-group').addClass('focused');
	    })
	    .on('focusout',function() {
	      if($(this).val() != ""){
	          //alert(1)
	         $(this).parents('.control-group').addClass('focused');
	        }else{
	          //alert(2)
	         $(this).parents('.control-group').removeClass('focused');
	        }
	    }); 
	
	  $(".control-group label").click(function(){
	      $(this).parents('.control-group').addClass('focused');
	      $(this).parents('.control-group').find('.form-control').focus();
	  });
	  
	  //// For multiple select
	  $('#participant_details').select2();
	  $('#SelectTechSkills').select2();
	  $('#applicant').select2();
	  $('#FormControlSelectSkill').select2();
		//Edit applicant submit
	  	$('#submit2').click(function(){
			if ((editNameError == true) && (editEmailError == true) && (editMobileError == true) && (editPhoneError == true) && (editQualificationError == true) || (editOtherQualificationError == true)) {
				
				swal({
					title: "Are you sure want to Proceed?",
					text: "",
					content: "Edit Applicant Submit",
					dangerMode: true,
					buttons: {
						confirm: { text: 'Yes, Submit', className: 'btn-success' },
						cancel: 'No'
					},
				})
					.then(function (isConfirm) {
						if (isConfirm) {
							$('#applicant_submit').submit();
							swal("Sucessfully Submitted ", {
								icon: "success",
							  });
  
						} else {
							swal.close();
						}
					});
			}
			return false;
		});
	});

	
	//meeting cancel
	$('.cancle_msg').click(function(){
		var self = $(this);
		var data = self.data();

		swal({
			title: "Are you sure want to cancel this meeting ?",
			text: "",
			content: "Cancel Message",
			dangerMode: true,
			buttons: {
				confirm: { text: 'Yes, Cancel', className: 'btn-success' },
				cancel: 'No'
			},
		})
			.then(function (isConfirm) {
				if (isConfirm) {
					console.log('data',$(this).data());
					session.rpc("/c/interview/cancel", {data : data})
					.then(function (result) {
						swal({
		        			title: result['error_msg'],
		        			text: "",
		        			content: result['error_msg'],
		        			dangerMode: true,
		        			buttons: {
		        				confirm: { text: 'ok', className: 'btn-success' }
		        			},
		        		})
		        			.then(function (isConfirm) {
		        				if (isConfirm) {
		        					location.reload();
		        				} 
		        		});
						
					});
				} else {
					swal.close();
				}
			});
	});

	$('#reset_form').click(function(){
		$(document).find('.clear').val(null);
	});

	$('#reset_applicant').click(function(){
		$(document).find('.clear').val(null);
	});
	//meeting submit
	$('#meetingSubmit').click(function(){
		checkSelect('#kw_start_meeting_date','#error-cYears');		
		checkSelect('#meeting_times','#error_time');
		checkSelect('#m-duration','#error_duration_msg');
		checkSelect('#moi','#error_moi');
		checkSelect('#participant_details','#error_panel');
		checkSelect('#applicant','#applicant_error');
		var v_date = $('#kw_start_meeting_date').val();
		var v_time = $('#meeting_times').val();
		var v_duration = $('#m-duration').val();
		var v_moi = $('#moi').val();
		var v_panel = $('#participant_details').val();
		var v_applicant = $('#applicant').val();
		if ($('#moi').val()=='face2face'){
			checkSelect('#location','#error_loc');
			var v_moi_f2f_loc = $('#location').val();
			if ($('#location').val()){
				checkSelect('#meeting_room','#error_room');
				var v_moi_f2f_room = $('#meeting_room').val();
			}
		}
		else if ($('#moi').val()=='telephonic'){
			var v_moi_ph = checkMobile('#ph_number','#ph_error_message');
			$('#error_loc').hide();
		}
		else if ($('#moi').val()=='videoconf'){
			var v_moi_url = checkUrl('#other_url_input','#error_url');
			console.log("url : ",v_moi_url);
			checkSelect('#location','#error_loc');
			var v_moi_f2f_loc = $('#location').val();
			if ($('#location').val()){
				checkSelect('#meeting_room','#error_room');
				var v_moi_f2f_room = $('#meeting_room').val();
			}
			if (v_moi_url!=true){
				v_moi_f2f_loc = false;
				v_moi_f2f_room = false;
			}
		}
		else{
			var v_moi_others = '00'
		}

		if ((v_date && v_time && v_duration && v_moi && v_moi_f2f_loc && v_moi_f2f_room && v_panel && v_applicant)||(v_date && v_time && v_duration && v_moi && v_moi_ph && v_panel && v_applicant)||(v_date && v_time && v_duration && v_moi && v_moi_ph && v_moi_url && v_panel && v_applicant)||(v_date && v_time && v_duration && v_moi && v_moi_others && v_panel && v_applicant)||(v_date && v_time && v_duration && v_moi && v_moi_f2f_loc && v_moi_f2f_room && v_moi_url && v_panel && v_applicant))
		{
			swal({
				title: "Are you sure want to Proceed?",
				text: "",
				content: "Submit meeting",
				dangerMode: true,
				buttons: {
					confirm: { text: 'Yes, Submit', className: 'btn-success' },
					cancel: 'No'
				},
			})
			.then(function (isConfirm) {
				if (isConfirm) {
					var indexed_array = {};
					$.map($('#schedule_meeting').serializeArray(), function(n, i){
						indexed_array[n['name']] = n['value'];
					});
					let action = $('#schedule_meeting').attr('action');
					jsonp(action,indexed_array);
				} else {
				  swal.close();
				}
				});	
		}
		
		
	});


	
	


	


	//Applicant Create Form Validation
	// Applicant submit
	$('#verifyCaptcha').click(function(){
	
		let ans = $('#answer').val();
        let captcha = $('#mathcaptcha').val();
        let applicantEdit = $('#editapplicant').val();
        if (applicantEdit){
        	addNameError = validateUsername('#cname','#name_message');
        	addEmailError = validateEmail('#cemail','#email_message');
        	addMobileError = checkMobile('#cmobile','#mobile_message');
        	addQualificationError = validateQualification('#FormControlSelectQuali','#qualification_message');
        	addResumeError = true;
        	addJobLocationError = checkSelect('#FormControlSelectJobLocation','#job_location_message');
        	addPhoneError = checkMobile('#cphone','#phone_message');
        	
        }
        if (addNameError && addEmailError && addMobileError  && addQualificationError && addResumeError && addJobLocationError || addPhoneError || addOtherQualificationError){
			
			if (ans && captcha) {
				if(ans!==captcha){
					$('#errorCaptcha').text('Captcha Mismatched');
					return false;
				}
			}else{
				if(!captcha){
					$('#errorCaptcha').text('Please Enter the Captcha!');
					return false;
				}
			}
			swal({
				title: "Are you sure want to Submit?",
				text: "",
				content: "Submit applicant details",
				dangerMode: true,
				buttons: {
					confirm: { text: 'Yes, Submit', className: 'btn-success' },
					cancel: 'No'
				},
			})
				.then(function (isConfirm) {
					if (isConfirm) {
						$.blockUI();
						var indexed_array = {};
					    $.map($('#CareerForm').serializeArray(), function(n, i){
					        indexed_array[n['name']] = n['value'];
					    });

					    var myFile = self.$('#fileDocument').prop('files')[0];
					    var action = $('#CareerForm').attr('action')
					    $("div.blockUI").remove();
					    if (myFile){
					    	var reader = new FileReader();
					    	reader.onload = function (e) {
			                	var data = reader.result;
			                	indexed_array['filename']= myFile['name'];
			                	indexed_array['file']= data;
			                	jsonp(action,indexed_array);
			                }
			                reader.readAsDataURL(myFile);
					    }else{
					    	jsonp(action,indexed_array);
					    }
					    
		                
		                
					} else {
						swal.close();
					}
				});
        }
		else{
			if (!addNameError && !applicantEdit) {
				$('#name_message').show();
			}
			if (!addEmailError && !applicantEdit) {
				$('#email_message').show();
			}
			if (!addMobileError && !applicantEdit) {
				$('#mobile_message').show();
			}
			if (!addPhoneError && !applicantEdit) {
				$('#phone_message').show();
			}
			if (!addQualificationError && !applicantEdit) {
				$('#qualification_message').show();
			}
			if (!addResumeError && !applicantEdit) {
				$('#resume_message').show();
			}
			if (!addOtherQualificationError && !applicantEdit) {
				$('#required_message').show();
			}
			if (!addJobLocationError && !applicantEdit) {
				$('#job_location_message').show();
			}
		}
		
	});
	

	//Validation Error Variables
	let addNameError = false;
	let editNameError = true;
	let addEmailError = false;
	let editEmailError = true;
	let addMobileError = false;
	let editMobileError = true;
	let addPhoneError = false;
	let editPhoneError = true;
	let addQualificationError = false;
	let editQualificationError = true;
	let addResumeError = false;
	let addOtherQualificationError = false;
	let addJobLocationError = false;

	//applicant name validation in add applicant form
	$('#name_message').hide();    
	$('#cname').keyup(function () {
		addNameError = validateUsername('#cname','#name_message');
	});

	//Applicant name validation in edit applicant form


	$('#name_error').hide();
	$('#editPartnerName').keyup(function () {
		editNameError = validateUsername('#editPartnerName','#name_error');
		console.log(editNameError)
	});

	
	function validateUsername(id,error_id) {
		let usernameValue = $(id).val();
		if (usernameValue == '') {
			$(error_id).show();
			return false;
		} 
		else if((usernameValue.length < 3)) {
			$(error_id).show();
			$(error_id).html("Applicant Name can't be less than 3 letters!");
			return false;
		} 
		else {
			$(error_id).hide();
			return true;
		}
	}
	//Applicant Email validation in add applicant form
	$('#email_message').hide();    
	
	$('#cemail').keyup(function () {
		addEmailError = validateEmail('#cemail','#email_message');
	});

	//Applicant Email validation in edit applicant form

	$('#email_error').hide();
	$('#editEmailFrom').keyup(function () {
		editEmailError = validateEmail('#editEmailFrom','#email_error');
	});

	function validateEmail(id,error_id){
		let email = $(id).val();
		let regex =/^([_\-\.0-9a-zA-Z]+)@([_\-\.0-9a-zA-Z]+)\.([a-zA-Z]){2,7}$/;
		if(email.match(regex)){
			$(error_id).hide();
			return true;
		}
		else if (email.length == 0) {
			$(error_id).html('Applicant Email is required!');
			$(error_id).show();
			return false;
		} 
		else{
			$(error_id).show();
			return false;
		}
	}

	//applicant Mobile validation
	$('#mobile_message').hide();    
	$('#cmobile').keyup(function () {
		addMobileError = checkMobile('#cmobile','#mobile_message');
	});

	$('#cphone').keyup(function () {
		addPhoneError = checkMobile('#cphone','#phone_message');
	});

	//Applicant mobile validation in edit applicant form

	$('#mobile_error').hide();
	$('#editPartnerMobile').keyup(function () {
		editMobileError = checkMobile('#editPartnerMobile','#mobile_error');
	});

	$('#editPartnerPhone').keyup(function () {
		editPhoneError = checkMobile('#editPartnerPhone','#alt_mobile_error');
	});
	
	
	
	function checkMobile(id,error_id) {
		let mobile = $(id).val();
		if (id == '#editPartnerPhone' || id == '#cphone') {
			if (mobile.length == 0) {
				$(error_id).hide();
				return false;
			}
		}
		if (mobile.length == 0) {
			$(error_id).show();
			$(error_id).html("Please Provide Your Phone Number Details!");
			return false;
		}
		if (mobile.length > 0) {
			if(!mobile.match(/^(\+\d{1,3}[- ]?)?\d{10}$/)){
				$(error_id).show();
				$(error_id).html("Enter valid Phone Number. ");
				return false;
			}
			else if (mobile.length < 8){
				$(error_id).show();
				$(error_id).html("Enter valid Phone Number.");
				
			}
			else{
				$(error_id).hide();
				return true;
			}
				
		}
    }

	function validateLocation() {
		let location = $('#FormControlSelectJobLocation').val();
		if (location.length == '') {
			$('#job_location_message').show();
			return false;
		} 
		else {
			$('#job_location_message').hide();
			return true;
		}
	}
	
	function validateResume() {
		let file = $('#fileDocument').val();
		
		if (!file) {
			$('#resume_message').show();
			return false;
		} 
		else {
			$('#resume_message').hide();
			return true;
		}
	}
	//Add applicant form qualification validation
	$('#qualification_message').hide();
	$('#FormControlSelectQuali').change(function(){
		addQualificationError = validateQualification('#FormControlSelectQuali','#qualification_message');
	})
	//Other qualification validation in Add applicant form
	$('#required_message').hide();
	$('#cQualificationT').keyup(function(){
		addOtherQualificationError = validateQualification('#cQualificationT','#required_message')
	})

	//edit applicant form qualification validation

	$('#qualification_error').hide();
	$('#EditFormControlSelectQuali').change(function(){

		editQualificationError = validateQualification('#EditFormControlSelectQuali','#qualification_error')
	})

	$('#other_required_message').hide();
	$('#otherQualificationT').change(function(){
		editOtherQualificationError = validateQualification('#otherQualificationT','#other_required_message')
	})

	function validateQualification(id,error_id) {
		let location = $(id).val();
		if (location.length == 0) {
			$(error_id).show();
			return false;
		} 
		else {
			$(error_id).hide();
			return true;
		}
	}



	$('#job_location_message').hide();
	$('#FormControlSelectJobLocation').change(function () {
		addJobLocationError = checkSelect('#FormControlSelectJobLocation','#job_location_message');
	});



	$('#tech_skill_message').hide();
	$('#skill_ids').change(function () {
		checkSelect('#skill_ids','#tech_skill_message');
	});

	$('#error-cYears').hide();									// meeting form validation -- date
	$('#kw_start_meeting_date').change(function () {
		checkSelect('#kw_start_meeting_date','#error-cYears');
	});

	$('#error_time').hide();								// meeting form validation -- time
	$('#meeting_times').change(function () {
		checkSelect('#meeting_times','#error_time');
	});

	$('#error_duration_msg').hide();								// meeting form validation -- durtion
	$('#m-duration').change(function () {
		checkSelect('#m-duration','#error_duration_msg');
	});

	$('#error_moi').hide();								// meeting form validation -- moi
	$('#moi').change(function () {
		checkSelect('#moi','#error_moi');
	});

	$('#error_loc').hide();								// meeting form validation--location
	
	$('#error_room').hide();

	$('#error_room').hide();								// meeting form validation--meeting room
	$('#meeting_room').change(function () {
		checkSelect('#meeting_room','#error_room');
	});

	$('#applicant_error').hide();								// meeting form validation--applicant
	$('#applicant').change(function () {
		checkSelect('#applicant','#applicant_error');
	});

	$('#error_panel').hide();									// meeting form validation--panel members



	console.log($('#applicant').val());
	
	function checkSelect(id,error_id){
		let element = $(id).val();
		console.log(element);
		if(element!=null){
			if(element.length==0){
			$(error_id).show();
			return false;
			}
			else{
				$(error_id).hide();
				return true;
			}
		}
		else{
			$(error_id).show();
			return false;
		}
		
	}


	$('#error_url').hide();						// meeting form validation--url
	$('#other_url_input').keyup(function () {
		checkUrl('#other_url_input','#error_url');
	});
	function checkUrl(id,error_id) {	
		let element = $(id).val();
		console.log(element);
		let regex = /(http|https):\/\/(\w+:{0,1}\w*)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%!\-\/]))?/;
		//  "((http|https)://)(www.)?" + "[a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]" + "{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)";
		
		if (element.length == 0){
			$(error_id).show();
			$(error_id).html("Url is Required!");
			return false;
		}
		else if(!element.match(regex)){
			$(error_id).show();
			$(error_id).html("Url is Invalid!");
			return false;
		}
		else {
			$(error_id).hide();
			return true;
		}
	}

	$('#resume_message').hide();
	$('#fileDocument').change(function () {
		$('#mainfileele').removeClass();
		$('#mainfileele').addClass('col-sm-12 col-md-12 col-lg-12');
		$('#namefileelm').remove();
		$('#mainfileele').removeAttr('id');
		if($(this).data()){
			console.log('skip validation');
			addResumeError = true;
		}else{
			addResumeError = checkLength('#fileDocument','#resume_message');
		}
		
	});
	
	function checkLength(id,error_id) {	
		let element = $(id).val();

		console.log(element.length);
		if (element.length == 0){
			$(error_id).show();
			return false;
		}
		else {
			$(error_id).hide();
			return true;
		}
       
    }
	
	

	$('#resume_message').hide();
	$('#fileDocument').change(function () {
		checkExtension('#fileDocument','#resume_message');
	});

	
	function checkExtension(id,error_id) { 
		let element = $(id).val();
		let x = element.split('.').pop();
		const extensions = ["pdf","doc","docx"]
		console.log(element.length);
		if (element.length == 0){
			$(error_id).show();
			$(error_id).html("Resume is Required!");
			return false;
		}
		else {
			$(error_id).hide();
			if(extensions.includes(x.toLowerCase())!=true){
				$(error_id).show();
				$(error_id).html("*.pdf, *.doc, *.docx File Only Supported!");
				return false;
			}
			else{
				$(error_id).hide();
				return true;
			}
		}
       
    }
	
	$('#location').on('change', function(){
		checkSelect('#location','#error_loc');						// meeting form validation--location
		session.rpc('/c/get_meeting_room', {data : this.value})				
		.then(function (result) {
			$('#meeting_room').empty();
			$('#meeting_room').append(new Option('',''))
			$.each(result['rooms'] , function(index, val) { 
				$('#meeting_room').append(new Option(val['name'], val['id']))
			});
		});

	});
});



