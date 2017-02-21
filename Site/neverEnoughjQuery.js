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
                $.ajax({
                    type: "GET",
                    dataType: "json",
                    withCredentials: true,
                    headers: {
                        'Authorization': 'Basic ' + btoa(user + ':' + pass)
                    },
                    url: "https://192.168.2.194:9020/esls/api/1.0/policies/" + policy_id,
                    success: function(data){
                        Materialize.showStaggeredList('#staggered-test');
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
                        energy_off_time.append(data[3]['time_h_off'] + ':' + data[3]['time_m_off'])
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded');
                        Materialize.showStaggeredList('#staggered-test'); //TEST
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
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
                var policy_id = document.getElementById("policy_on_id").value;
                var policy_intensity = document.getElementById("policy_on_intensity").value;
                var policy_h = document.getElementById("policy_on_time_h").value;
                var policy_m = document.getElementById("policy_on_time_m").value;
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
                    url: "https://192.168.2.194:9020/esls/api/1.0/policies/lamp/" + policy_id + "/on",
                    success: function(msg){
                        alert( "Data Saved: " + msg );
                        Materialize.toast('Data saved!', 4000, 'rounded')
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded')
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
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
                var policy_id = document.getElementById("policy_off_id").value;
                var policy_h = document.getElementById("policy_off_time_h").value;
                var policy_m = document.getElementById("policy_off_time_m").value;
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
                    url: "https://192.168.2.194:9020/esls/api/1.0/policies/lamp/" + policy_id + "/off",
                    success: function(msg){
                        alert( "Data Saved: " + msg );
                        Materialize.toast('Data saved!', 4000, 'rounded')
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded')
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
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
                var energy_id = document.getElementById("energy_id").value;
                var energy_intensity = document.getElementById("energy_intensity").value;
                var energy_h_on = document.getElementById("energy_time_h_on").value;
                var energy_m_on = document.getElementById("energy_time_m_on").value;
                var energy_h_off = document.getElementById("energy_time_h_off").value;
                var energy_m_off = document.getElementById("energy_time_m_off").value;
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
                    url: "https://192.168.2.194:9020/esls/api/1.0/policies/lamp/" + energy_id + "/energy",
                    success: function(msg){
                        alert( "Data Saved: " + msg );
                        Materialize.toast('Data saved!', 4000, 'rounded')
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        Materialize.toast('ERROR HTTP ' + XMLHttpRequest.status, 4000, 'rounded')
                    }
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
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
            }
        },
        messages: {
            user: {
                required: "Username required"
            },
            password: {
                required: "Password required"
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
            policy_off_time_h: {
                required: true,
                range: [0, 23]
            },
            policy_off_time_m: {
                required: true,
                range: [0, 59]
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
            policy_off_time_h: {
                required: "Time h required",
                range: "Must be a number in range 0-23"
            },
            policy_off_time_m: {
                required: "Time m required",
                range: "Must be a number in range 0-59"
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
            policy_on_time_h: {
                required: true,
                range: [0, 23]
            },
            policy_on_time_m: {
                required: true,
                range: [0, 59]
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
            policy_on_time_h: {
                required: "Time h required",
                range: "Must be a number in range 0-23"
            },
            policy_on_time_m: {
                required: "Time m required",
                range: "Must be a number in range 0-59"
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
            energy_time_h_on: {
                required: true,
                range: [0, 23]
            },
            energy_time_m_on: {
                required: true,
                range: [0, 59]
            },
            energy_time_h_off: {
                required: true,
                range: [0, 23]
            },
            energy_time_m_off: {
                required: true,
                range: [0, 59]
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
            energy_time_h_on: {
                required: "Time h required",
                range: "Must be a number in range 0-23"
            },
            energy_time_m_on: {
                required: "Time m required",
                range: "Must be a number in range 0-59"
            },
            energy_time_h_off: {
                required: "Time h required",
                range: "Must be a number in range 0-23"
            },
            energy_time_m_off: {
                required: "Time m required",
                range: "Must be a number in range 0-59"
            }
        }
    });
});
