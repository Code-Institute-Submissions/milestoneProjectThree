$(document).ready(function () {
    $(".sidenav").sidenav();
    $(".tooltipped").tooltip();
    $("input#username, input#password, input#confirm-password, input#first_name, input#last_name").characterCounter();
});

// $('.button-collapse').sidenav({
//       menuWidth: 300, // Default is 240
//       edge: 'left', // Choose the horizontal origin
//       closeOnClick: true // Closes side-nav on <a> clicks
//     }
//   );
