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
    $('#methods_group .btn').on('click',function(e){
        setTimeout(count);
    })
    var count =  function(){
        var val = '';
        $('#methods_group .btn').each(function(i, btn){
            if($(btn).hasClass('active') ){
                val += '' + $(btn).data('wat');
            }
        });
        $('#hierHier').html(val); 
    }
});