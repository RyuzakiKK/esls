$(document).ready(function() {
    $('#ajax').click(function(){
        var user = document.getElementById("user").value;
        var pass = document.getElementById("password").value
         $.ajax({
            type: "GET",
            dataType: "json",
            withCredentials: true,
            headers: {
                'Authorization': 'Basic ' + btoa(user + ':' + pass)
            },
            url: "https://192.168.2.194:9020/esls/api/v0.1/policies/1",
        }).then(function(data) {
            alert(data)
            $('.greeting-id').append(data.id);
            $('.greeting-content').append(data.content);
        });
    });
    
    $("#password").keyup(function(event){
        if(event.keyCode == 13){
            $("#ajax").click();
        }
    });
});
