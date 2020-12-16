$(document).ready(function() {
        
    // Initiate Edit Drink Selected from Dropdown
    $(document).on('change', '#select_drink', function() {
        var drink_id = $('#select_drink').val();

        if(drink_id === 'none') {
            $('#edit_drink_card').hide();
        } else if (drink_id === 'add') {
            // Add Drink Selected, create empty DB entry and display card
            req = $.ajax({
                url : '/recipe',
                type : 'POST',
                data : { drink_add : true }
            });

            req.done(function(data) {
                $('#edit_drink_card').fadeOut(100).fadeIn(1000);
                $('#edit_drink_card').html(data);
            });

        } else {
            // Drink Selected, Grab from database and display card
            req = $.ajax({
                url : '/recipe',
                type : 'POST',
                data : {drink_edit : true, drink_id : drink_id }
            });

            req.done(function(data) {
                $('#edit_drink_card').fadeOut(100).fadeIn(1000);
                $('#edit_drink_card').html(data);
            });
        };
    });

    // Upload New Image

    // Select Existing Image
    $(document).on('click', '.drinkImgBrowse', function() {
        var drink_id = $(this).attr('drink_id');
        var image_id = $(this).attr('image_id');

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_img_sel : true, drink_id : drink_id, image_id : image_id }
        });

        req.done(function(data) {
            $('#drink_image').attr('src', 'static/'+image_id);
        });

    });


    // Delete Drink
    $(document).on('click', '.drinkDelButton', function() {
        var drink_id = $(this).attr('drink_id');

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_del : true, drink_id : drink_id }
        });

        req.done(function(data) {
            $('#edit_drink_card').hide();
        });

    });

    // Update Drink ID
    $(document).on('click', '.drinkIDButton', function() {
        var drink_id = $(this).attr('drink_id');
        var new_drink_id = $('#new_drink_id').val();
        console.log(drink_id);
        console.log(new_drink_id);
        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_edid : true, drink_id : drink_id, new_drink_id : new_drink_id }
        });

        req.done(function(data) {
            $('#edit_drink_card').fadeOut(100).fadeIn(1000);
            $('#edit_drink_card').html(data);
            console.log('Edited drink ID.')
        });
    });

    // Update Display Name
    $(document).on('click', '.drinkDNButton', function() {
        var drink_id = $(this).attr('drink_id');
        var new_drink_dn = $('#new_drink_dn').val();
        console.log(drink_id);
        console.log(new_drink_dn);
        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_dn : true, drink_id : drink_id, new_drink_dn : new_drink_dn }
        });

        req.done(function(data) {
            //$('#edit_drink_card').hide();
            console.log('Edit drink Display Name.')
        });

    });

    // Update Drink Description
    $(document).on('click', '.drinkDescButton', function() {
        var drink_id = $(this).attr('drink_id');
        var new_drink_desc = $('#new_drink_desc').val();
        console.log(drink_id);
        console.log(new_drink_desc);
        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_desc : true, drink_id : drink_id, new_drink_desc : new_drink_desc }
        });

        req.done(function(data) {
            //$('#edit_drink_card').hide();
            console.log('Edit drink Description.')
        });

    });

    // Edit Drink Ingredient 
    $(document).on('click', '.drinkIngEditButton', function() {
        var drink_id = $(this).attr('drink_id');
        var ing_id = $(this).attr('ing_id');
        console.log(drink_id);
        console.log(ing_id);
        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_ing_edit : true, drink_id : drink_id, ing_id : ing_id }
        });

        req.done(function(data) {
            $('#drink_ing_ID_'+ing_id).fadeOut(100);
            $('#drink_ing_ID_'+ing_id).html(data).fadeIn(1000);
            console.log('Edit ingredient.')
        });
    });

    // Delete Drink Ingredient 
    $(document).on('click', '.drinkIngDelButton', function() {
        var drink_id = $(this).attr('drink_id');
        var ing_id = $(this).attr('ing_id');
        console.log(drink_id);
        console.log(ing_id);

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_ing_del : true, drink_id : drink_id, ing_id : ing_id }
        });

        req.done(function(data) {
            $('#drink_ing_ID_'+ing_id).remove();

            // Grab new ADD data html and refresh it
            nreq = $.ajax({
                url : '/recipe',
                type : 'POST',
                data : {drink_ing_add_init : true, drink_id : drink_id }
            });
            
            nreq.done(function(data) { 
                $('#drink_ing_ADD').html(data);
            });
        });

    });

    // Save Drink Ingredient 
    $(document).on('click', '.drinkIngSaveButton', function() {
        var drink_id = $(this).attr('drink_id');
        var ing_id = $(this).attr('ing_id');
        var new_pumptime = $('#pumptime_'+ing_id).val();
        console.log(drink_id);
        console.log(ing_id);
        console.log(new_pumptime);

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_ing_save : true, drink_id : drink_id, ing_id : ing_id, new_pumptime : new_pumptime }
        });

        req.done(function(data) {
            $('#drink_ing_ID_'+ing_id).fadeOut(100);
            $('#drink_ing_ID_'+ing_id).html(data).fadeIn(1000);
            console.log('Saved ingredient change.')
        });

    });

    // Add Drink Ingredient 
    $(document).on('click', '.drinkIngAddButton', function() {
        var drink_id = $(this).attr('drink_id');
        var new_ing_id = $('#drink_ing_id_ADD').val();
        var new_pumptime = $('#new_drink_ing_pumptime').val();
        console.log(drink_id);

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {drink_ing_add : true, drink_id : drink_id, new_ing_id : new_ing_id, new_pumptime : new_pumptime }
        });

        req.done(function(data) {
            // Grab added data and add it to the table before the ADD line
            $('#drink_ing_ADD').before('<tr id=\"drink_ing_ID_'+new_ing_id+'\"></tr>')
            $('#drink_ing_ID_'+new_ing_id).html(data).fadeIn(1000);

            // Grab new ADD data html and append
            nreq = $.ajax({
                url : '/recipe',
                type : 'POST',
                data : {drink_ing_add_init : true, drink_id : drink_id }
            });
            
            nreq.done(function(data) { 
                $('#drink_ing_ADD').html(data);
            });

        });
    });
});