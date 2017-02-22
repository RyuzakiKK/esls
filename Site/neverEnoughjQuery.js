$(document).ready(function() {

    var lamp_id = $('.lamp_id');
    var policy_on_intensity = $('.policy_on_intensity');
    var policy_on_time = $('.policy_on_time');
    var policy_off_time = $('.policy_off_time');
    var policy_on_photoresistor = $('.policy_on_photoresistor');
    var policy_off_photoresistor = $('.policy_off_photoresistor');
    var energy_intensity = $('.energy_intensity');
    var energy_on_time = $('.energy_on_time');
    var energy_off_time =  $('.energy_off_time');
    var login_form = $('#login_form');
    var port = ":9020";

    $(function() {
        $('#login_form').on('submit', function(e) {
            e.preventDefault();
        });
    });

    $(function() {
        $('#get_form').on('submit', function(e) {
            e.preventDefault();
            if (document.getElementById("policy_id").value === "getRandomNumber()") {
                document.getElementById("policy_id").value = 4; // chosen by fair dice roll. Guaranteed to be random.
                                                                // https://xkcd.com/221
            }
            var fail = false;
            login_form.find('input').each(function(){
                if($(this).prop('required')){
                    if (!$(this).val()) {
                        fail = true
                    }
                }
            });
            if (!fail) {
                var user = document.getElementById("user").value;
                var pass = document.getElementById("password").value;
                var policy_id = document.getElementById("policy_id").value;
                var address = document.getElementById("address").value;
                if (address.length < 5 || address.substring(0, 4) != "http") {
                    address = "https://" + address;
                }
                $.ajax({
                    type: "GET",
                    dataType: "json",
                    withCredentials: true,
                    headers: {
                        'Authorization': 'Basic ' + btoa(user + ':' + pass)
                    },
                    url: address + port + "/esls/api/1.0/policies/" + policy_id,
                    success: function(data){
                        lamp_id.empty();
                        lamp_id.append(data[0]);
                        policy_on_intensity.empty();
                        policy_on_intensity.append(data[1]['intensity']);
                        policy_on_time.empty();
                        policy_on_time.append(data[1]['time_h'] + ':' + data[1]['time_m']);
                        policy_off_time.empty();
                        policy_off_time.append(data[2]['time_h'] + ':' + data[2]['time_m']);
                        policy_on_photoresistor.empty();
                        policy_on_photoresistor.append(data[1]['photoresistor']);
                        policy_off_photoresistor.empty();
                        policy_off_photoresistor.append(data[2]['photoresistor']);
                        energy_intensity.empty();
                        energy_intensity.append(data[3]['intensity']);
                        energy_on_time.empty();
                        energy_on_time.append(data[3]['time_h_on'] + ':' + data[3]['time_m_on']);
                        energy_off_time.empty();
                        energy_off_time.append(data[3]['time_h_off'] + ':' + data[3]['time_m_off']);
                        Materialize.showStaggeredList('#staggered');
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded');
                        $('#staggered').css({opacity: 0});
                        console.log(XMLHttpRequest.status + " " + textStatus + " " + errorThrown);
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Check the Credential fields
            }
        });
    });

    $(function() {
        $('#policy_on_form').on('submit', function(e) {
            e.preventDefault();
            var fail = false;
            login_form.find('input').each(function(){
                if($(this).prop('required')){
                    if (!$(this).val()) {
                        fail = true
                    }
                }
            });
            if (!fail) {
                var user = document.getElementById("user").value;
                var pass = document.getElementById("password").value;
                var address = document.getElementById("address").value;
                if (address.length < 5 || address.substring(0, 4) != "http") {
                    address = "https://" + address;
                }
                var policy_id = document.getElementById("policy_on_id").value;
                var policy_intensity = document.getElementById("policy_on_intensity").value;
                var array_time = document.getElementById("policy_on_time").value.split(':');
                var policy_h = array_time[0];
                var policy_m = array_time[1];
                var policy_photoresistor = document.getElementById("policy_on_photoresistor").value;
                var data = {"intensity":policy_intensity,"time_h":policy_h,"time_m":policy_m,"photoresistor":policy_photoresistor};
                data = JSON.stringify(data);
                console.log(data);
                $.ajax({
                    type: "POST",
                    contentType : 'application/json',
                    data: data,
                    withCredentials: true,
                    headers: {
                        'Authorization': 'Basic ' + btoa(user + ':' + pass)
                    },
                    url: address + port + "/esls/api/1.0/policies/lamp/" + policy_id + "/on",
                    success: function(msg){
                        Materialize.toast('Data saved!', 4000, 'rounded');
                        console.log(msg);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded');
                        console.log(XMLHttpRequest.status + " " + textStatus + " " + errorThrown);
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Check the Credential fields
            }
        });
    });

    $(function() {
        $('#policy_off_form').on('submit', function(e) {
            e.preventDefault();
            var fail = false;
            login_form.find('input').each(function(){
                if($(this).prop('required')){
                    if (!$(this).val()) {
                        fail = true
                    }
                }
            });
            if (!fail) {
                var user = document.getElementById("user").value;
                var pass = document.getElementById("password").value;
                var address = document.getElementById("address").value;
                if (address.length < 5 || address.substring(0, 4) != "http") {
                    address = "https://" + address;
                }
                var policy_id = document.getElementById("policy_off_id").value;
                var array_time = document.getElementById("policy_off_time").value.split(':');
                var policy_h = array_time[0];
                var policy_m = array_time[1];
                var policy_photoresistor = document.getElementById("policy_off_photoresistor").value;
                var data = {"time_h":policy_h,"time_m":policy_m,"photoresistor":policy_photoresistor};
                data = JSON.stringify(data);
                console.log(data);
                $.ajax({
                    type: "POST",
                    contentType : 'application/json',
                    data: data,
                    withCredentials: true,
                    headers: {
                        'Authorization': 'Basic ' + btoa(user + ':' + pass)
                    },
                    url: address + port + "/esls/api/1.0/policies/lamp/" + policy_id + "/off",
                    success: function(msg){
                        Materialize.toast('Data saved!', 4000, 'rounded');
                        console.log(msg);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded');
                        console.log(XMLHttpRequest.status + " " + textStatus + " " + errorThrown);
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Check the Credential fields
            }
        });
    });
    
    $(function() {
        $('#energy_form').on('submit', function(e) {
            e.preventDefault();
            var fail = false;
            login_form.find('input').each(function(){
                if($(this).prop('required')){
                    if (!$(this).val()) {
                        fail = true
                    }
                }
            });
            if (!fail) {
                var user = document.getElementById("user").value;
                var pass = document.getElementById("password").value;
                var address = document.getElementById("address").value;
                if (address.length < 5 || address.substring(0, 4) != "http") {
                    address = "https://" + address;
                }
                var energy_id = document.getElementById("energy_id").value;
                var energy_intensity = document.getElementById("energy_intensity").value;
                var array_time_on = document.getElementById("energy_time_on").value.split(':');
                var energy_h_on = array_time_on[0];
                var energy_m_on = array_time_on[1];
                var array_time_off = document.getElementById("energy_time_off").value.split(':');
                var energy_h_off = array_time_off[0];
                var energy_m_off = array_time_off[1];
                var data = {"intensity":energy_intensity,"time_h_on":energy_h_on,"time_m_on":energy_m_on,"time_h_off":energy_h_off,"time_m_off":energy_m_off};
                data = JSON.stringify(data);
                console.log(data);
                $.ajax({
                    type: "POST",
                    contentType : 'application/json',
                    data: data,
                    withCredentials: true,
                    headers: {
                        'Authorization': 'Basic ' + btoa(user + ':' + pass)
                    },
                    url: address + port + "/esls/api/1.0/policies/lamp/" + energy_id + "/energy",
                    success: function(msg){
                        Materialize.toast('Data saved!', 4000, 'rounded');
                        console.log(msg);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded');
                        console.log(XMLHttpRequest.status + " " + textStatus + " " + errorThrown);
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Check the Credential fields
            }
        });
    });

    $.validator.setDefaults({
        errorClass: 'invalid',
        validClass: "valid",
        errorPlacement: function (error, element) {
            $(element)
                .closest("form")
                .find("label[for='" + element.attr("id") + "']")
                .attr('data-error', error.text());
        },
        submitHandler: function (form) {
            console.log('form ok');
        }
    });

    $("form[id='login_form']").validate({
        rules: {
            user: {
                required: true
            },
            password: {
                required: true
            },
            address: {
                required: true
            }
        },
        messages: {
            user: {
                required: "Username required"
            },
            password: {
                required: "Password required"
            },
            address: {
                required: "Address required"
            }
        }
    });

    $("form[id='get_form']").validate({
        rules: {
            policy_id: {
                required: true,
                number: true
            }
        },
        messages: {
            policy_id: {
                required: "Policy id required",
                number: "Only number allowed"
            }
        }
    });

    $("form[id='policy_off_form']").validate({
        rules: {
            policy_off_id: {
                required: true,
                number: true
            },
            policy_off_time: {
                required: true,
                time: true
            },
            policy_off_photoresistor: {
                required: true,
                range: [0, 100]
            }
        },
        messages: {
            policy_on_id: {
                required: "Policy id required",
                number: "Only number allowed"
            },
            policy_off_time: {
                required: "Time required",
                time: "Must be of the format hh:mm"
            },
            policy_off_photoresistor: {
                required: "Photoresistor required",
                range: "Must be a number in the range 0-100"
            }
        }
    });

    $("form[id='policy_on_form']").validate({
        rules: {
            policy_on_id: {
                required: true,
                number: true
            },
            policy_on_intensity: {
                required: true,
                range: [0, 100]
            },
            policy_on_time: {
                required: true,
                time: true
            },
            policy_on_photoresistor: {
                required: true,
                range: [0, 100]
            }
        },
        messages: {
            policy_on_id: {
                required: "Policy id required",
                number: "Only number allowed"
            },
            policy_on_intensity: {
                required: "Intensity required",
                range: "Must be a number in range 0-100"
            },
            policy_on_time: {
                required: "Time h required",
                time: "Must be of the format hh:mm"
            },
            policy_on_photoresistor: {
                required: "Photoresistor required",
                range: "Must be a number in range 0-100"
            }
        }
    });

    $("form[id='energy_form']").validate({
        rules: {
            energy_id: {
                required: true,
                number: true
            },
            energy_intensity: {
                required: true,
                range: [0, 100]
            },
            energy_time_on: {
                required: true,
                time: true
            },
            energy_time_off: {
                required: true,
                time: true
            }
        },
        messages: {
            energy_id: {
                required: "Policy id required",
                number: "Only number allowed"
            },
            energy_intensity: {
                required: "Intensity required",
                range: "Must be a number in range 0-100"
            },
            energy_time_on: {
                required: "Time h required",
                time: "Must be of the format hh:mm"
            },
            energy_time_off: {
                required: "Time h required",
                time: "Must be of the format hh:mm"
            }
        }
    });
});
