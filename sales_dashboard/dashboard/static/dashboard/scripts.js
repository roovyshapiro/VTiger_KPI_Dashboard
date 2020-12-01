var countdown_timer;
var countdown_update_label_timer;
var refresh_minutes;
var refresh_seconds;
var checkbox_status;
var date;


//WHEN the page reloads reload the values from local storage
//retrieve_saved_data will also continue the countdown timer
//if the checkbox was enabled before the page was reloaded
window.onload = retrieve_saved_data;

//Called when the page is reloaded
function retrieve_saved_data() {
    checkbox_status = localStorage.getItem("checkbox_status");
    checkbox_status_bool = (checkbox_status == 'true');
    refresh_minutes = localStorage.getItem("refresh_minutes");
    refresh_seconds = refresh_minutes * 60;
    localStorage.setItem("refresh_seconds", refresh_seconds);
    document.getElementById("minutes_input").value = refresh_minutes;
    document.getElementById("checkbox_autoupdate").checked = checkbox_status_bool;
    //Get the previously selected date, or get today's date
    retrieve_date();
    //If the checkbox is already clicked when the page reloads
    if (checkbox_status_bool){
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh: ' + refresh_seconds;
        checkbox_click();
    }
}

//
//
//   AUTO-REFRESH BOX + MINUTES SELECTOR
//
//

//WHEN the auto refresh check box is clicked
function checkbox_click() {
    checkbox_status = document.getElementById("checkbox_autoupdate").checked;
    localStorage.setItem("checkbox_status", checkbox_status);
    if (refresh_minutes == '' || refresh_minutes == null){
        document.getElementById("minutes_input").value = 10;
        update_refresh_time();
    }
    if (checkbox_status == true){
        countdown_timer = setTimeout(function() {
            location.reload();
        }, refresh_seconds * 1000);
        countdown_update();
    } else {
        clearTimeout(countdown_timer);
        clearInterval(countdown_update_label_timer);
        refresh_minutes = document.getElementById("minutes_input").value;
        refresh_seconds = refresh_minutes * 60; 
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh';

    }
}

//WHEN the number input field is changed
function update_refresh_time() {
    refresh_minutes = document.getElementById("minutes_input").value;
    refresh_seconds = refresh_minutes * 60; 
    localStorage.setItem("refresh_seconds", refresh_seconds);
    localStorage.setItem("refresh_minutes", refresh_minutes);
    clearTimeout(countdown_timer);
    clearInterval(countdown_update_label_timer);
    checkbox_click();
}

//While countdown_timer starts a one time countdown to refresh the page,
//countdown_update_label_timer starts an interval timer that shows
//how much time is remaining before the page refreshes 
function countdown_update(){
    refresh_seconds = parseInt(localStorage.getItem("refresh_seconds"));
    countdown_update_label_timer = setInterval(function(){
        refresh_seconds -= 1;
        if (refresh_seconds < 1){
            clearInterval(countdown_update_label_timer);
        }
        localStorage.setItem('refresh_seconds', refresh_seconds);
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh: ' + refresh_seconds;
    }, 1000);
}

//
//
//   DATE PICKER
//
//

//Every time the date is changed, update local storage
function date_changed(){
    var date = document.getElementById('datepicker').value;
    localStorage.setItem('date', date);
}

/*
//Set the previously selected date. If none, then choose today's date.
//Today's date is the default date.
function retrieve_date(){
    date = localStorage.getItem('date');
    if (date == '' || date == undefined){
        date = date_picker_today();
        localStorage.setItem('date', date);
    }
    date = localStorage.getItem('date');
    document.getElementById('datepicker').value = date;
}

//Returns today's date as a value formatted for datepicker.
function date_picker_today(){
    var date_today = new Date();
    var day = date_today.getDate();
    var month = date_today.getMonth() + 1;
    var year = date_today.getFullYear();
    if (month < 10) month = "0" + month;
    if (day < 10) day = "0" + day;
    var today = year + "-" + month + "-" + day;
    return today;
}
*/