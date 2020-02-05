/* -----  AUTO-UPDATE CHECKBOX  -----*/

//The amount of time in seconds until the page reloads
var update_time = 20;
//After a page reload, set the checkbox status to what's saved in localStorage
window.onload = function set_check_box() {
    var checked_status = JSON.parse(localStorage.getItem("checkbox_autoupdate"));
    document.getElementById("checkbox_autoupdate").checked = checked_status;
    localStorage.setItem("refresh_count", (this.update_time));
    autorefresh();
}
//Saves the current checkbox state to localStorage
function save() {	
	var checkbox = document.getElementById("checkbox_autoupdate");
    localStorage.setItem("checkbox_autoupdate", checkbox.checked);	
}
//If the checkbox is checked, '/populate' will be called after ten minutes.
function autorefresh() {
    save();
    var isChecked = document.getElementById("checkbox_autoupdate").checked;
    if (isChecked == true) {
        refresh_counter();
        time = setInterval(function () {
            window.location.assign("http://127.0.0.1:8000/populate");
        }, (update_time * 1000));
    } else if (isChecked == false) {
        clearInterval(time);
        clearTimeout(timeoutVar);
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh';
        localStorage.setItem("refresh_count", (this.update_time));
    }
}
autorefresh();
document.getElementById('checkbox_autoupdate').addEventListener('click', autorefresh);

//This function displays how many seconds remain until the page is auto-refreshed
function refresh_counter() {
        var refresh_count_int = JSON.parse(localStorage.getItem("refresh_count"));
        refresh_count_int = refresh_count_int - 1;
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh: ' + refresh_count_int;
        localStorage.setItem("refresh_count", refresh_count_int);
        if (refresh_count_int > 0){
            console.log(refresh_count_int)
            timeoutVar = setTimeout(refresh_counter, 1000);
        }
}


