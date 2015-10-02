$( document ).ready(function() {
    $( "#clear" ).click(function( event ) {
        $( "#timevsconc" ).text('')
        event.preventDefault();
    });
    $( "#demo" ).click(function( event ) {
        $( "#timevsconc" ).text('SOme text')
        event.preventDefault();
    });
});