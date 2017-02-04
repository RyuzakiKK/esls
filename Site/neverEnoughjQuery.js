$(document).ready(function() {
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/" + policy_id,
        }).then(function(data) {
            $('.lamp-id').empty()
            $('.lamp-id').append(data[0])
            $('.policy-on-intensity').empty()
            $('.policy-on-intensity').append(data[1]['intensity'])
            $('.policy-on-time').empty()
            $('.policy-on-time').append(data[1]['time_h'] + ':' + data[1]['time_m'])
            $('.policy-off-time').empty()
            $('.policy-off-time').append(data[2]['time_h'] + ':' + data[2]['time_m'])
            $('.policy-on-photoresistor').empty()
            $('.policy-on-photoresistor').append(data[1]['photoresistor'])
            $('.policy-off-photoresistor').empty()
            $('.policy-off-photoresistor').append(data[2]['photoresistor'])
            $('.energy-intensity').empty()
            $('.energy-intensity').append(data[3]['intensity'])
            $('.energy-on-time').empty()
            $('.energy-on-time').append(data[3]['time_h_on'] + ':' + data[3]['time_m_on'])
            $('.energy-off-time').empty()
            $('.energy-off-time').append(data[3]['time_h_off'] + ':' + data[3]['time_m_off'])
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
    
    $('#energy-post').click(function(){
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + energy_id + "/energy",
        }).then(function(data) {
            console.log(data);
        });
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + policy_id + "/on",
        }).then(function(data) {
            console.log(data);
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
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/lamp/" + policy_id + "/off",
        }).then(function(data) {
            console.log(data);
        });
    });
});
