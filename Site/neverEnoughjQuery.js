$(document).ready(function() {

    var lamp_id = $('.lamp-id');
    var policy_on_intensity = $('.policy-on-intensity');
    var policy_on_time = $('.policy-on-time');
    var policy_off_time = $('.policy-off-time');
    var policy_on_photoresistor = $('.policy-on-photoresistor');
    var policy_off_photoresistor = $('.policy-off-photoresistor');
    var energy_intensity = $('.energy-intensity');
    var energy_on_time = $('.energy-on-time');
    var energy_off_time =  $('.energy-off-time');
    var login_form = $('#login_form')

    $('#policy-get').click(function(){
        var user = document.getElementById("user").value;
        var pass = document.getElementById("password").value;
        var policy_id = document.getElementById("policy-id").value;
        $.ajax({
            type: "GET",
            dataType: "json",
            withCredentials: true,
            headers: {
                'Authorization': 'Basic ' + btoa(user + ':' + pass)
            },
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/" + policy_id
        }).then(function(data) {
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
        });
    });
    
    $("#password").keyup(function(event){
        if(event.keyCode == 13){
            $("#policy-id").click();
        }
    });
    
    $("#energy-time-m-off").keyup(function(event){
        if(event.keyCode == 13){
            $("#energy-post").click();
        }
    });
    
    $('#policy-on-post').click(function(){
        var user = document.getElementById("user").value;
        var pass = document.getElementById("password").value;
        var policy_id = document.getElementById("policy-on-id").value;
        var policy_intensity = document.getElementById("policy-on-intensity").value;
        var policy_h = document.getElementById("policy-on-time-h").value;
        var policy_m = document.getElementById("policy-on-time-m").value;
        var policy_photoresistor = document.getElementById("policy-on-photoresistor").value;
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + policy_id + "/on"
        }).then(function(data) {
            console.log(data);
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
                var policy_id = document.getElementById("policy-on-id").value;
                var policy_intensity = document.getElementById("policy-on-intensity").value;
                var policy_h = document.getElementById("policy-on-time-h").value;
                var policy_m = document.getElementById("policy-on-time-m").value;
                var policy_photoresistor = document.getElementById("policy-on-photoresistor").value;
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
                    url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + policy_id + "/on"
                }).then(function(data) {
                    console.log(data);
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
            }
        });
    });
    
    $('#policy-off-post').click(function(){
        var user = document.getElementById("user").value;
        var pass = document.getElementById("password").value;
        var policy_id = document.getElementById("policy-off-id").value;
        var policy_h = document.getElementById("policy-off-time-h").value;
        var policy_m = document.getElementById("policy-off-time-m").value;
        var policy_photoresistor = document.getElementById("policy-off-photoresistor").value;
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + policy_id + "/off"
        }).then(function(data) {
            console.log(data);
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
                var energy_id = document.getElementById("energy-id").value;
                var energy_intensity = document.getElementById("energy-intensity").value;
                var energy_h_on = document.getElementById("energy-time-h-on").value;
                var energy_m_on = document.getElementById("energy-time-m-on").value;
                var energy_h_off = document.getElementById("energy-time-h-off").value;
                var energy_m_off = document.getElementById("energy-time-m-off").value;
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
                    url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + energy_id + "/energy"
                }).then(function(data) {
                    console.log(data);
                });
            } else {
                console.log("required fields!!");
                login_form.find(':submit').click(); // Display the default "required" message
            }
        });
    });
});
