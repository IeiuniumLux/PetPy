(function pullImage() {
    document.querySelector(".login").addEventListener('click', getToken);})();

function getToken(obj) {
    // var loginUrl = "http://petpy.net"
    var xhr = new XMLHttpRequest();
    var passwordElement = document.getElementById('password');
    var password = passwordElement.value;
    
    xhr.open('POST', '/login');
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function() {
        var responseObject = JSON.parse(this.response);
        console.log(responseObject);
        if (responseObject.token) {
            console.log(responseObject.token);
        } else {
            console.log("No token received");
        }
    });
    
    xhr.send(JSON.stringify({password: password}));
}
