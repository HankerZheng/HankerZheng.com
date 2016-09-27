"use strict";
// reposition modal
function reposition() {
    var modal = $(".modal"),
        dialog = modal.find('.modal-dialog'),
        thisImg = dialog.find('img');
    modal.css('display', 'block');
    dialog.css('min-width', $(window).width()*0.7);
    thisImg.css('max-height', $(window).height()*0.9);
    dialog.css("margin-top", Math.max(0, ($(window).height() - dialog.height()) / 2));
}

$(window).on('resize', function() {
    $('.modal:visible').each(reposition);
});

$.fn.bsPhotoGallery = function() {
    var clicked = {};

    function showHideControls(){
      var total = $('.photo-gallery li').length;
  		if(total === clicked.nextImg){
  			$('.bsp-controls.next').hide();
  		}else{
  			$('.bsp-controls.next').show()
  		}
  		if(clicked.prevImg === -1){
  			$('.bsp-controls.previous').hide();
  		}else{
  			$('.bsp-controls.previous').show()
  		}
  	}
    // add modal info
    // this function is called by `$('.li').on('click', showModal)`
    // therefore `this` in the function is `<li>`
    function showModal(){      
        var theImg = $(this).find('img');
        var src = theImg.attr('src');
        var largeImg = theImg.attr('data-bsp-large-src');
        if(typeof largeImg === 'string'){
              src = largeImg;
        }
        var index = $(this).attr('data-bsp-li-index');
        var pText = theImg.attr('myTitle');        
        var modalText = typeof pText !== 'undefined' ? pText : 'undefined';
        var alt =  typeof theImg.attr('alt') == 'string' ? theImg.attr('alt') : null;
        
        clicked.img = src;
        clicked.prevImg = parseInt(index) - parseInt(1);
    		clicked.nextImg = parseInt(index) + parseInt(1);
        $('#bsPhotoGalleryModal').modal();
        var html = '';
        $('#bsPhotoGalleryModal .modal-body img').attr('src', clicked.img);
        
        if(alt !== null){
          html += '<h4>'+alt+'</h4>'
        }
        if(typeof pText !== 'undefined'){
          html += '<p class="pText">'+pText+'</p>'
        }
        $('.modal-body .next').attr("href", clicked.nextImg)
        $('.modal-body .previous').attr("href", clicked.prevImg)
        $('.bsp-text-container').html(html);
        showHideControls();
        $('.modal-body img').load(function(){
          reposition();
        });
    }

    function nextPrevHandler(){
        var index = $(this).attr('href');
        var src = $('li[data-bsp-li-index="'+index+'"] img').attr('src')
        var largeImg = $('li[data-bsp-li-index="'+index+'"] img').attr('data-bsp-large-src');

        if(typeof largeImg === 'string'){
              src = largeImg;
        }        
        var pText = $('li[data-bsp-li-index="'+index+'"] img').attr('myTitle');        
        var modalText = typeof pText !== 'undefined' ? pText : 'undefined';
        var theImg = $('li[data-bsp-li-index="'+index+'"] img');
        var alt =  typeof theImg.attr('alt') == 'string' ? theImg.attr('alt') : null;
         
        $('.modal-body img').attr('src', src);
        var txt = '';
        if(alt !== null){
          txt += '<h4>'+alt+'</h4>'
        }
        if(typeof pText !== 'undefined'){
          txt += '<p class="pText">'+pText+'</p>'
        }        
        
        $('.bsp-text-container').html(txt); 
        $('.modal-body img').load(function(){
          reposition();
        });

        clicked.prevImg = parseInt(index) - 1;
        clicked.nextImg = parseInt(clicked.prevImg) + 2;

        if($(this).hasClass('previous')){
            $(this).attr('href', clicked.prevImg);
            $('a.next').attr('href', clicked.nextImg);
        }else{
            $(this).attr('href', clicked.nextImg);
            $('a.previous').attr('href', clicked.prevImg);
        }
      showHideControls();
      return false;
    }
    function resetClicked(){
      clicked = {};
    }

    var items = $(this).find('li');
    items.each(function(x){
      var theImg = $(this).find('img');
      if (theImg.attr('src').startsWith("/static/photos")){
        var original = theImg.attr('src').split('_')[0];
        theImg.attr('data-bsp-large-src', original+'_large.jpg');
      }
      $(this).addClass('bspHasModal');
      $(this).on('click', showModal);
    });
    $('a.bsp-controls').on('click', nextPrevHandler);
    $(document).on('hidden.bs.modal', resetClicked);

    return this;
};