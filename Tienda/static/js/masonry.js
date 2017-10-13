
$( document ).ready(function() {
    jQuery('.item-masonry').hover(
    function(){
      $(this).find(".cover-item-gallery").fadeIn();
    },
    function(){
      $(this).find(".cover-item-gallery").fadeOut();
    }
    );

    var sizer = '.sizer4';

    var container = $('#gallery');

    container.imagesLoaded(function(){
      container.masonry({
        itemSelector: '.item-masonry',
        columnWidth: sizer,
        percentPosition: true
      });
    });
});
