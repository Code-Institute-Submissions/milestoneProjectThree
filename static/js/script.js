$(document).ready(function () {

    // Materialize utilities
    $(".sidenav").sidenav();
    $(".tooltipped").tooltip();
    $("input#username, input#password, input#confirm-password, input#first_name, input#last_name, input#title_name, input#title_name, input#release_year, textarea#description, input#genre, input#director, input#cast, input#duration, input#library_name").characterCounter();
    $("select").formSelect();
    $('.modal').modal();
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 5,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });

    // Set 4 second timeout against flash messages
    setTimeout(function() {
    $('#flash-section').fadeOut('fast');
    }, 4000); 
    
});
