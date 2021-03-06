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
  
  // --- header search form --- //
  // $('.header-search-handler').on('click', function(){
  //   $('.user-nav').find('li.dropdown').removeClass('open');
  //   $('.header-search-wrap').toggle();
  // })
  
  // --- SLIDESHOW --- //
  $('.sujet').bjqs({
    'height' : 308,
    'width' : 519,
    'responsive' : true,
    'showcontrols' : false,
    'animspeed' : 5000,
    'showmarkers' : false
  });
  
  // --- LAYOUT --- //
  $('.sr-filter-handler').on('click', function(){
    $('.sr-filter-container').slideToggle(300);
  })
  
  
  
  
  // --- LAYOUT --- //
  if ($(window).width() > 480) {
    $('.header-search-wrap').removeClass('dropdown-menu');
    $('.header-search-handler').hide();
  
  }
  
  // --- HACKS --- //
  // fixes bug where dropdown-links aren't fired on touch devices
  $('body').on('touchstart.dropdown', '.dropdown-menu', function (e) { e.stopPropagation(); });
  
  


})