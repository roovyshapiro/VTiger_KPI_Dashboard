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
    console.log(all_products);
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
        //If its 01-01, set date to Dec 31
        chosen_date.setDate(chosen_date.getDate() - 1);
        }

    else if(timeframe=='tomorrow'){
        var today = new Date();
        //var tomorrow = new Date();
        //Don't allow user to choose a date in the future
        //end the function now so it doesn't refresh the page
        //for no reason.
        if(chosen_date > today  || chosen_date == today){
            return;
        } else{
            chosen_date.setDate(chosen_date.getDate() + 1);
        }
    }

    //1 -> 01, 3 -> 03, etc.
    var day = chosen_date.getDate();
    if(day.toString().length == 1){
        day = `0${day}`;
    }
    //1 -> 01, 3 -> 03 etc.
   var month = chosen_date.getMonth() + 1;
   if(month.toString().length == 1){
        month = `0${month}`;
    }

    new_date = `${chosen_date.getFullYear()}-${month}-${day}`;
    localStorage.setItem('selected_date', new_date);
    document.getElementById("date_start").value = new_date;
    save_group_date();
}

//https://datatables.net/
//Scrollable Tables have been replaced with Data Tables
//which provide far more functionality including
//sorting, filtering & choosing how many rows to load
$(document).ready( function () {
    $('table.scrollable_table').DataTable();
} );


/* 
With the use of JSON Script we can get data from the Django model and then
access it with JS
https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#json-script
*/
function print_product(){
    //Get a json object of all the products which was passed from the view
    var all_products = JSON.parse(document.getElementById('products_json').textContent);
    //https://i.imgur.com/BOQ1hq1.png
    //that screenshow shows what the structure of the "all_products" json object is
    console.log(all_products);

    //find the dropdown and get the selection as the product_name
    var item = document.getElementById('product_dropdown');
    var product_name= item.options[item.selectedIndex].text;

    //the all_products json object is structured like {product_name:{name:' ', weight: ' ', etc.}}
    //so we use the name of the product as the index of the all_products json object
    console.log('product_name from selection dropdown', product_name);
    console.log('when you use the name as the index of the all_products json object', all_products[product_name]);

    //now we can access the product's attributes from the json object
    console.log('name', all_products[product_name].name);
    console.log('width', all_products[product_name].width);
    console.log('length', all_products[product_name].length);
    console.log('height', all_products[product_name].height);
}

/* 

Using the historical case data of groups and displaying them as 
a bar chart using chartjs. 
Note: Kill Rate is commented out as it is a percentage value.
If a group has a large amount of cases, the kill rate bar will appear
small, and vice versae. It negatively impacts the look of the chart
but may be useful in the future.
https://www.chartjs.org/docs/latest/getting-started/
https://codepen.io/bencarmichael/pen/XeYJXJ


*/
var data_history = JSON.parse(document.getElementById('historical_data').textContent);
console.log(data_history);
var selected_history_group = localStorage.getItem("selected_group");

var years = Object.keys(data_history);
var date_label = [];
var group_created = [];
var group_resolved = [];
//var group_kill_rate = [];
for (year in years){
    var months = Object.keys(data_history[years[year]]);
	for (month in months){
        date_label.push(`${years[year]} - ${data_history[years[year]][months[month]]['month']}`);
        group_created.push(data_history[years[year]][months[month]]['created_groups'][selected_history_group]['created']);
        group_resolved.push(data_history[years[year]][months[month]]['created_groups'][selected_history_group]['resolved']);
        //group_kill_rate.push(data_history[years[year]][months[month]]['created_groups'][selected_history_group]['kill_rate']);
	}
}

var barChartData = {
    labels: date_label,
    datasets: [
      {
        label: "Created",
        backgroundColor: "lightblue",
        borderColor: "blue",
        borderWidth: 1,
        data: group_created
      },
      {
        label: "Resolved",
        backgroundColor: "pink",
        borderColor: "red",
        borderWidth: 1,
        data: group_resolved,
      },
      /*{
        label: "Kill Rate %",
        backgroundColor: "#FFDEAD",
        borderColor: "#FF7518",
        borderWidth: 1,
        data: group_kill_rate,
      },*/
    ]
  };
  
  var chartOptions = {
    responsive: true,
    legend: {
      position: "top"
    },
    title: {
      display: true,
      text: "Chart.js Bar Chart"
    },
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
  
  window.onload = function() {
    var ctx = document.getElementById("group_chart").getContext("2d");
    window.myBar = new Chart(ctx, {
      type: "bar",
      data: barChartData,
      options: chartOptions
    });
  };

/*
Showing how the current groups case data compares to the past 3 months

https://www.chartjs.org/docs/latest/charts/line.html

const labels = Utils.months({count: 7});
const data = {
  labels: labels,
  datasets: [{
    label: 'March',
    data: [2, 4, 80,],
    fill: false,
    borderColor: '#DCDCDC',
    tension: 0.2
  },
  {
    label: 'April',
    data: [7, 46, 45, 23, 2, 23, 11],
    fill: false,
    borderColor: '#D0D0D0',
    tension: 0.2
  },
  {
    label: 'May',
    data: [25, 4, 7, 45, 43, 22, 11],
    fill: false,
    borderColor: '#A9A9A9',
    tension: 0.2
  },
  {
    label: 'June',
    data: [65, 59, 80, 81, 56, 55, 40],
    fill: false,
    borderColor: '#000000',
    tension: 0.2
  },]
};
  
*/
