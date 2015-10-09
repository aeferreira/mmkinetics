$( document ).ready(function() {
    $( "#input_clear" ).click(function( event ) {
        $( "#timevsconc" ).text('');
        event.preventDefault();
    });
    $("#input_demo").bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/_demodata', {},
        function(data) {
        $("#timevsconc").text(data.result);
      });
      return false;
    });
});