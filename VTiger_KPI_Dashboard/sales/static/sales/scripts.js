var countdown_timer;
var countdown_update_label_timer;
var refresh_minutes;
var refresh_seconds;
var checkbox_status;
var selected_group;
var selected_date;

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
    //If the checkbox is already clicked when the page reloads
    if (checkbox_status_bool){
        document.getElementById("auto_update_label").innerHTML = 'Auto Refresh: ' + refresh_seconds;
        checkbox_click();
    }
    //Put in today's date into the date selector unless a date has been chosen already
    if (localStorage.getItem("selected_date") == null){
        var today = new Date();
        var today_date = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
        document.getElementById("date_start").value = today_date;
    } else {
        document.getElementById("date_start").value = localStorage.getItem("selected_date");
    }
    //Set group dropdown but only for case dashboard
    //If there's no group dropdown selected, then set it to "All Groups" by default
    if (window.location.href.includes('/cases')){
        if (localStorage.getItem("selected_group") == null){
            document.getElementById("group_dropdown").value = "All Groups";
            localStorage.setItem("selected_group", "All Groups");
        } else {
            document.getElementById("group_dropdown").value = localStorage.getItem("selected_group");
        }
        //If a group is selected, and the user then navigates away from cases, when he comes back
        //to cases, all groups are displayed even though a different group is selected in the drop
        //down. To resolve this, the form is Quickly resubmitted with the selected group.
        //With this method, the chosen group is maintained even when navigating away from cases.
        if (document.getElementById('group_name').innerHTML != localStorage.getItem("selected_group")){
            console.log(document.getElementById('group_name').innerHTML);
            console.log(localStorage.getItem("selected_group"));
            document.getElementById("date_group_form").submit();
        }
    }
    console.log(localStorage);
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

//When the submit button is clicked on the Case Dashboard, the 
//date and group are saved to localstorage so it can be retrieved
//after the page is reloaded. Sales dashboard utilizies date as well.
function save_group_date(){
    selected_group = document.getElementById("group_dropdown");
    if(selected_group){
        selected_group = document.getElementById("group_dropdown").value;
        localStorage.setItem("selected_group", selected_group);
    }

    selected_date = document.getElementById('date_start').value;
    localStorage.setItem("selected_date", selected_date);
    console.log(localStorage);
    document.getElementById("date_group_form").submit();

}

//This function is called when the arrows are clicked next to the timechanger
//to change the date back and forth by one day. This automatically submits the page
//as the submit function was moved to save_group_date()
function date_changer(timeframe){
    //["2020", "12", "15"]
    var chosen_date_arr = localStorage.getItem('selected_date').split('-');
    //Tue Dec 15 2020 00:00:00 GMT-0500 (Eastern Standard Time)
    chosen_date = new Date(`${chosen_date_arr[0]},${chosen_date_arr[1]},${chosen_date_arr[2]}`);

    if(timeframe=='yesterday'){
        var timediff = chosen_date.getDate() - 1;
    }
    else if(timeframe=='tomorrow'){

        var today = new Date();
        //Don't allow user to choose a date in the future
        //end the function now so it doesn't refresh the page
        //for no reason.
        if (chosen_date.getDate() + 1 > today.getDate()){
            return;
        }
        else{
            var timediff = chosen_date.getDate() + 1;
        }
    }
    //9 -> 09 , 3 -> 03, etc.
    if(timediff.toString().length == 1){
        timediff = `0${timediff}`;
    }
    new_date = `${chosen_date.getFullYear()}-${chosen_date.getMonth() + 1}-${timediff}`;
    localStorage.setItem('selected_date', new_date);
    document.getElementById("date_start").value = new_date;
    save_group_date();
}