$(document).ready(function () {
    $(".sidenav").sidenav();
    $(".tooltipped").tooltip();
    $("input#username, input#password, input#confirm-password, input#first_name, input#last_name").characterCounter();
    $("select").formSelect();
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 5,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
});



// $('.button-collapse').sidenav({
//       menuWidth: 300, // Default is 240
//       edge: 'left', // Choose the horizontal origin
//       closeOnClick: true // Closes side-nav on <a> clicks
//     }
//   );
