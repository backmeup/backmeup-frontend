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
  



})