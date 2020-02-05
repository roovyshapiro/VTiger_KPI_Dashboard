// AUTO-UPDATE CHECKBOX 

//After a page reload, set the checkbox status to what's saved in localStorage
window.onload = function set_check_box() {
    var checked_status = JSON.parse(localStorage.getItem("checkbox_autoupdate"));
    document.getElementById("checkbox_autoupdate").checked = checked_status;
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
        time = setInterval(function () {
            window.location.assign("http://127.0.0.1:8000/populate");
        }, 600000);

    } else if (isChecked == false) {
        clearInterval(time);
    }
}
autorefresh();
document.getElementById('checkbox_autoupdate').addEventListener('click', autorefresh);


