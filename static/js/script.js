$(function(){
  
  $('.dropdown-toggle').dropdown();
  
  // --- Dashboard
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
  // open delete-backup-overlay-form
  // $('.delete-backup-handler').on('click', function(e){
  //   e.preventDefault();
  //   $(this).closest('li').find('.delete-backup-overlay').show();
  // })
  



})