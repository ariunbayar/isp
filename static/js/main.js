$(function() {
    $('button.close').click(function(){
        $(this).parent().hide(500);
    });
});

$(function() {
    $("#expire_date").datetimepicker({
        dateFormat: 'yy-mm-dd',
        timeFormat: 'HH:mm'
    });
}); 
