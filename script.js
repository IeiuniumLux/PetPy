(function pullImage() {
    var date = new Date();
    document.getElementById('cam').src = '[YOUR PORT FORWARDING IP or DNS' + parseInt(date.getTime()/1000);
    setTimeout(pullImage, 600);})();

function feed(obj) {
    var xhr; 
    if (window.XMLHttpRequest) 
        xhr = new XMLHttpRequest(); 
    else if (window.ActiveXObject) 
        xhr = new ActiveXObject("Msxml2.XMLHTTP");
    else 
        throw new Error("Ajax is not supported by your browser");

    var date = new Date();
    var path_info = 'feed/' + ((parseInt(date.getTime()/1000) - 946684800) - (date.getTimezoneOffset() * 60));
    
    // Handle response from server asynchronously
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("lastfeed").innerHTML = 'Nom nom! Thanks!'
        }
    };
    xhr.open("GET", path_info);
    xhr.send();
    obj.disabled = true;
    setTimeout(function() {
        obj.disabled = false;
    }, 500);
}

document.querySelector("button.feed").addEventListener('click', feed);