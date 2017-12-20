(function pullImage() {
    var date = new Date();
    document.getElementById('cam').src = 'http://petpy.net/' + parseInt(date.getTime()/1000);
    setTimeout(pullImage, 600);})();

function feed(obj) {
    var xhr; 
    if (window.XMLHttpRequest) 
        xhr = new XMLHttpRequest(); 
    else 
        throw new Error("Ajax is not supported by your browser");

    var date = new Date();
    var path_info = 'feed/' + ((parseInt(date.getTime()/1000) - 946684800) - (date.getTimezoneOffset() * 60));
    
    xhr.open("GET", path_info);
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("lastfeed").innerHTML = 'Nom nom! Thanks!'
        }
    };
    xhr.send();
    obj.disabled = true;
    setTimeout(function() {
        obj.disabled = false;
    }, 400);
}

document.querySelector(".feed").addEventListener('click', feed);