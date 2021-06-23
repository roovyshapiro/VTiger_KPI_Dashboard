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
try{
  var data_history = JSON.parse(document.getElementById('historical_data').textContent);
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
      maintainAspectRatio: false,
      legend: {
        position: "top"
      },  
      plugins:{
        title: {
          display: true,
          text: "Created/Resolved for all Months"
        },
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
} catch(err){
  console.log('group chart not available for all groups', err);
}


/*
Showing how the current groups case data compares to the past 3 months
https://www.chartjs.org/docs/latest/charts/line.html

Example of Data:
    {
    June':{
        'first_day': datetime.datetime(2021, 6, 1, 0, 0, tzinfo=<UTC>),
        'last_day': datetime.datetime(2021, 6, 30, 23, 59, 59, tzinfo=<UTC>), 
        'resolved': [6, 6, 6, 10, 0, 0, 6, 6, 7, 7, 6, 0, 0, 6, 4, 7, 3, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }, 
    'May':{
        'first_day': datetime.datetime(2021, 5, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 5, 31, 0, 0, tzinfo=<UTC>), 
        'resolved': [0, 0, 5, 7, 8, 7, 7, 0, 0, 7, 6, 9, 6, 5, 0, 0, 7, 3, 4, 11, 2, 0, 0, 19, 7, 2, 7, 2, 3, 0, 0]
    }, 
    'April': {
        'first_day': datetime.datetime(2021, 4, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 4, 30, 0, 0, tzinfo=<UTC>), 
        'resolved': [9, 3, 0, 0, 11, 6, 3, 7, 4, 1, 0, 4, 1, 12, 3, 6, 0, 0, 20, 5, 9, 6, 12, 0, 1, 9, 5, 6, 5, 0]
        }, 
    'March': {
        'first_day': datetime.datetime(2021, 3, 1, 0, 0, tzinfo=<UTC>), 
        'last_day': datetime.datetime(2021, 3, 31, 0, 0, tzinfo=<UTC>), 
        'resolved': [10, 16, 3, 8, 0, 2, 1, 11, 9, 9, 6, 16, 0, 0, 11, 7, 9, 8, 1, 0, 0, 6, 5, 5, 4, 24, 0,0, 9, 4, 0]
        }
    }

    Resolved Case Line Chart
*/
try{
  var month_comparison = JSON.parse(document.getElementById('month_comparison').textContent);

  var months = Object.keys(month_comparison);
  var colors = ['#933d41', '#fc6c85', '#ffb6c1', '#ffe4e1'] ;
  
  var line_chart_data = {};
  line_chart_data['datasets'] = [];
  for (month in months) {
    line_chart_data['datasets'].push(
      {
        label: months[month],
        data: month_comparison[months[month]]['resolved'],
        fill:false,
        tension: 0.2,
        borderColor: colors[month],
      }
    );
  }
  
  var date_labels = [];
  for (var i = 1; i <= 31; i++) {
    date_labels.push(i);
  }
  line_chart_data['labels']  = date_labels;
  
  var lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    pointHitRadius:15,
    pointRadius:4,
    legend: {
      position: "top"
    },
    plugins:{
      title: {
        display: true,
        text: "Resolved per day VS Previous 4 Months"
      },
    },
  };
  
  var lineChartConfig = {
    type: "line",
    data: line_chart_data,
    options: lineChartOptions
  };
  
  var lineChart = new Chart(
    document.getElementById('month_comparison_chart'),
    lineChartConfig
  );
}catch(err){
  console.log('resolved case chart not available for all groups', err);
}



/* Created Case Line Chart */

try{
  var month_comparison_created = JSON.parse(document.getElementById('month_comparison_created').textContent);

  var created_months = Object.keys(month_comparison_created);
  var created_colors = ['#191970', '#1e90ff', '#87cefa', '#ace5ee' ];
  
  var line_chart_data_created = {};
  line_chart_data_created['datasets'] = [];
  for (month in created_months) {
    line_chart_data_created['datasets'].push(
      {
        label: created_months[month],
        data: month_comparison_created[created_months[month]]['created'],
        fill:false,
        tension: 0.2,
        borderColor: created_colors[month],
      }
    );
  }
  line_chart_data_created['labels']  = date_labels;
  
  var lineChartOptionsCreated = {
    responsive: true,
    maintainAspectRatio: false,
    pointHitRadius:15,
    pointRadius:4,
    legend: {
      position: "top"
    },
    plugins:{
      title: {
        display: true,
        text: "Created per day VS Previous 4 Months"
      },
    },
  };
  
  var lineChartConfigCreated = {
    type: "line",
    data: line_chart_data_created,
    options: lineChartOptionsCreated
  };
  
  var lineChartCreated = new Chart(
    document.getElementById('month_comparison_created_chart'),
    lineChartConfigCreated
  );
  
}catch(err){
  console.log('created chart not available for all groups', err);
}

/* User Assigned Total Open Doughnut Chart

*/
//There's a variable amount of users, so depending on how many users there are
//That's how many random colors get generated and added to the doughnut chart data set
var dynamicColors = function() {
  var r = Math.floor(Math.random() * 255);
  var g = Math.floor(Math.random() * 255);
  var b = Math.floor(Math.random() * 255);
  return "rgb(" + r + "," + g + "," + b + ")";
};
var backgroundColorArray = [];

var user_assigned_total_open = JSON.parse(document.getElementById('user_assigned_total_open').textContent);
var users_assigned = Object.keys(user_assigned_total_open);

//var user_colors = ['#191970', '#1e90ff', '#87cefa', '#ace5ee' ];
var users_assigned_amount = []
for (user in users_assigned){
  users_assigned_amount.push(user_assigned_total_open[users_assigned[user]]);
  backgroundColorArray.push(dynamicColors());
}

var user_assigned_data = {
  labels: users_assigned,
  datasets: [{
    label: 'Doughnut Chart',
    data: users_assigned_amount,
    backgroundColor: backgroundColorArray,
    hoverOffset: 4
  }]
};

var user_assigned_options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins:{
    title: {
      display: true,
      text: "Open Assigned Per User"
    },
    legend: {
      position: "left"
    },  
  },
};

var user_assigned_config = {
  type: 'doughnut',
  data: user_assigned_data,
  options: user_assigned_options,
};


var doughnutChartAssigned = new Chart(
    document.getElementById('user_assigned_total_open_chart'),
  user_assigned_config
);