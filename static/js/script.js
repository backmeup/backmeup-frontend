$(function(){
  
  $('.dropdown-toggle').dropdown();
  
  // --- DASHBOARD --- //
  // if backuplist is smaller than n items: show details per default;
  if ($('.backup-list').children().length < 3){
    $('.backup-list').find('.backup-summary, .backup-details').toggle();
    $('.backup-details-handler').addClass('open');
  }
  // show/hide backup-details on click
  $('.backup-details-handler').on('click', function(e){
    e.preventDefault();
    $(this).toggleClass('open').closest('li').find('.backup-summary, .backup-details').slideToggle();
  })
  
  // remove django-messages on click
  $('.messages').on('click', '.close', function(){
    var msg_list = $(this).closest('.messages');
    if($(msg_list).children().length == 1){
      $(msg_list).fadeOut(300, function() {
        $(msg_list).remove();
      })
    }
    else{
      $(this).closest('li').fadeOut(300, function() {
        $(this).closest('li').remove();
      });
    }
  })
  



})