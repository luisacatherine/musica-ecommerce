$('.flip').hover(function(){
    $(this).find('.card').toggleClass('flipped');
});

$('#modalSignUp').on('shown.bs.modal', function () {
    $('#signUp').trigger('focus')
})

function changeImage(id_image){
    image = document.getElementById('imgDisp');
    var x = image.getAttribute("src")
    var y = id_image.src
    image.src = y
    id_image.src = x
}

function logOut(){
    
}