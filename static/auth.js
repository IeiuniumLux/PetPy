function getToken(obj) {
    var xhr = new XMLHttpRequest();
    var passwordElement = document.getElementById('login-pass');
    var password = passwordElement.value;
    
    xhr.open('POST', '/login');
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = '/';
        } else if (this.readyState == 4 && this.status == 401) {
            document.getElementById("auth-failed").innerHTML = 'Authentication Failed. Please try again.'
        }
    };
    xhr.send(JSON.stringify({password: password}));
}

document.querySelector(".btn").addEventListener('click', getToken);