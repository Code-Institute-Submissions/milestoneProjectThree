$(document).ready(function () {
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

    // set 4 second timeout against flash messages
    setTimeout(function() {
    $('#flash-section').fadeOut('fast');
    }, 4000); 

    // $("#imdb_search_btn").click(function(){
    //     var title_text = $("#title_name").val();
        // var title_year  = $("#release_year").val();
        // search_string = title_text + " " + title_year;
        // alert(title_text);
        // imdb_search(search_string);
        
        // $.post("{{ url_for('imdb_search') }}", {title_text});
        //  $.post("{{ url_for('imdb_search', title_text=title_text) }}");
    // });
   
//     $("#imdb_search_btn").click(function(){
//     var $this = $("#title_name").val();
//     $.ajax({
//       url: "{{ url_for('imdb_search') }}",
//       data: $this,
//       method: "POST",
//       success: function(data) {
//           console.log($this)
//         //Here if u have to do something with the response
//       }
//     });
//   })

    
        // $("#imdb_search_btn").bind('click', function(){
        //     $.getJSON('/imdbsearch', {
        //         title_text : $("#title_name").val()
        //     }, function (data) {
        //         $("#result").text(data.result);
        //     });
        //     return false;
        // });
    


    // Tutorial script to resolve materialize select validation issue 
    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
});
