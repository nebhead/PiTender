$(document).ready(function() {
        
    // Initiate Edit Ingredient
    $(document).on('click', '.ingrEditButton', function() {
        var ing_id = $(this).attr('ing_id');

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {ing_edit : true, ing_id : ing_id }
        });

        req.done(function(data) {
            $('#ing_row_ID_'+ing_id).html(data);
            $('#ing_row_ID_'+ing_id).fadeIn(1000);
        });

    });

    // Delete Ingredient
    $(document).on('click', '.ingrDelButton', function() {
        var ing_id = $(this).attr('ing_id');

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : {ing_del : true, ing_id : ing_id }
        });

        req.done(function(data) {
            $('#ing_row_ID_'+ing_id).remove();
        });

    });

    // Save Ingredient
    $(document).on('click', '.ingrSaveButton', function() {
        var ing_id = $(this).attr('ing_id');
       
        var ing_new_id = $('#ing_new_id_'+ing_id).val();
        
        var ing_new_dn = $('#ing_new_dn_'+ing_id).val();

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : { ing_save : true, ing_id : ing_id, ing_new_id : ing_new_id, ing_new_dn : ing_new_dn }
        });

        req.done(function(data) {
            $('#ing_row_ID_'+ing_id).html(data);
            $('#ing_row_ID_'+ing_id).fadeIn(1000);
            var ing_new_id_returned = $('#old_ing_id_'+ing_id).attr('new_ing_id');
            console.log('New ID Returned: ' + ing_new_id_returned);
            if ( ing_new_id_returned != ing_new_id) {
                ing_new_id = ing_new_id_returned;
            }
            $('#ing_row_ID_'+ing_id).attr('id','ing_row_ID_'+ing_new_id);
            $('#old_ing_id_'+ing_id).attr('id', 'edited');
        });
    });

    // Add Ingredient
    $(document).on('click', '.ingrAddButton', function() {
        var ing_id = 'ing_row_add'
        var ing_new_id = $('#add_id').val();
        var ing_new_dn = $('#add_dn').val();

        req = $.ajax({
            url : '/recipe',
            type : 'POST',
            data : { ing_add : true, ing_new_id : ing_new_id, ing_new_dn : ing_new_dn }
        });

        req.done(function(data) {
            $('#ing_row_add').html(data);
            $('#ing_row_add').fadeIn(1000);
            // Rename the default ADD row with the new ID
            console.log('Looking for #old_ing_id_'+ing_id)
            var ing_new_id_returned = $('#old_ing_id_'+ing_id).attr('new_ing_id');
            console.log('New ID Returned: ' + ing_new_id_returned);
            if ( ing_new_id_returned != ing_new_id) {
                ing_new_id = ing_new_id_returned;
            }
            $('#ing_row_add').attr('id','ing_row_ID_'+ing_new_id);
            $('#old_ing_id_'+ing_id).attr('id', 'edited');
            
            // Add a new row to the end of the table for new input
            $('#ing_row_ID_'+ing_new_id).after('\
                <tr id=\"ing_row_add\">\
                    <td>\
                        <input type=\"text\" class=\"form-control\" id=\"add_id\" name=\"new_id\" placeholder=\"add ingredient id\">\
                    </td>\
                    <td>\
                        <input type=\"text\" class=\"form-control\" id=\"add_dn\" name=\"new_dn\" placeholder=\"add ingredient display name\">\
                    </td>\
                    <td>\
                        <button type=\"button\" class=\"btn text-success ingrAddButton\"><i class=\"far fa-plus-square\"></i></button>\
                    </td>\
                </tr>\
            ');
        });
    });

});