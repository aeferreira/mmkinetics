$( document ).ready(function() {
    $( "#input_clear" ).click(function( event ) {
        $( "#timevsconc" ).text('');
        event.preventDefault();
    });
    
    $( "#input_demo" ).click(function( event ) {
        var demo_data = "# demo data\n" + 
                        "0.00858 0.05\n" +
                        "0.01688 0.1\n" +
                        "0.02489 0.25\n" +
                        "0.03032 0.5\n" +
                        "0.03543 1\n" +
                        "0.03447 2.5\n" +
                        "0.03993 5";
        $( "#timevsconc" ).text(demo_data);
        event.preventDefault();
    });
    
});