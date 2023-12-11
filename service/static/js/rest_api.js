$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.wishlist_name);
        $("#wishlist_customer_id").val(res.customer_id)
        $("#wishlist_is_public").prop("checked", res.is_public);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_name").val("");
        $("#wishlist_id").val("");
        $("#wishlist_customer_id").val("")
        $("#wishlist_is_public").prop("checked", false)
        clear_wishlist_item_form()
        clear_wishlist_item_table()
    }

    // clears wishlist item form
    function clear_wishlist_item_form() {
        const selectors = [
            "#item_id",
            "#item_wishlist_id",
            "#item_product_id",
            "#item_product_name",
            "#item_price",
            "#item_quantity"
        ]

        selectors.forEach( selector => $(selector).val(""))

        // set wishlist_id into item form in case there is one loaded into
        // wishlist form
        $("#item_wishlist_id").val($("#wishlist_id").val())

    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // clear wishlist item table
    function clear_wishlist_item_table(){
        $("#wishlist-item-table tbody").empty()
    }

    // Render list of items in a given wishlist
    // function render_wishlist_item_table(res){
    //     for res.items
    // }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        let isPublic = $("#wishlist_is_public").is(":checked")
        
        let data = {
            "wishlist_name": $("#wishlist_name").val(),
            "customer_id": $("#wishlist_customer_id").val(),
            "is_public": isPublic,
            "created_date": (new Date()).toISOString()
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            //update_form_data(res)
            $("#wishlist_id").val(res.id)
            $("#item_wishlist_id").val(res.id)
            flash_message("Successfully created Wishlist with ID " + res.id)
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        let pet_id = $("#pet_id").val();
        let name = $("#pet_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";
        let gender = $("#pet_gender").val();
        let birthday = $("#pet_birthday").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "gender": gender,
            "birthday": birthday
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/pets/${pet_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    // Reusable function to retrieve and update wishlist information
    function retrieveAndUpdateWishlist(wishlist_id, shouldFlashSuccess) {
        return new Promise((resolve, reject) => {
            $("#flash_message").empty();
    
            let ajax = $.ajax({
                type: "GET",
                url: `/wishlists/${wishlist_id}`,
            });
    
            ajax.done(function(res) {
                clear_form_data();
                update_form_data(res);
                $("#item_wishlist_id").val(res.id);
                if (shouldFlashSuccess) {
                    flash_message("Success");
                }
                $.ajax({
                    type: "GET",
                    url: `/wishlists/${res.id}/items`,
                }).done(function(res) {
                    $("#wishlist-items-table tbody").empty();
                    if (res.length > 0) {
                        // create a table row for each item in the retrieved wishlist
                        $.each(res, function(index, item) {
                            $("#wishlist-items-table tbody").append(`<tr>
                                <td>${item.id}</td>
                                <td>${item.product_id}</td>
                                <td>${item.product_name}</td>
                                <td>${item.product_price}</td>
                                <td>${item.quantity}</td>
                                <td class="item-actions">
                                    <button class="btn btn-sm btn-default item-edit-btn" data-wishlist-and-item-id="${item.wishlist_id}:${item.id}">Edit</button>
                                    <button class="btn btn-sm btn-danger item-delete-btn" data-wishlist-and-item-id="${item.wishlist_id}:${item.id}">Delete</button>
                                </td>
                            </tr>`);
                        });
                    }
                    resolve(res); // Resolve the promise when the asynchronous operations are done
                });
            });
    
            ajax.fail(function(res) {
                clear_form_data();
                flash_message(res.responseJSON.message);
                reject(res); // Reject the promise in case of failure
            });
        });
    }

    $("#retrieve-btn").click(async function () {
        let wishlist_id = $("#wishlist_id").val();
        try {
            let result = await retrieveAndUpdateWishlist(wishlist_id, true);
        } catch (error) {
            // Handle error
            flash_message("unexpected error has ocurred when calling retrieveAndUpdateWishlist");
        }
    });

    // ****************************************
    // Delete a wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            if (res.status == 204)
            {
                clear_form_data()
                flash_message("Wishlist with ID " + wishlist_id + " not found")
            }
            else
            {
                clear_form_data()
                flash_message("Successfully deleted Wishlist with ID " + wishlist_id)
            }
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Wishlist by Customer ID
    // TODO
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#pet_name").val();
        let category = $("#pet_category").val();
        let available = $("#pet_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">Birthday</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.category}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.birthday}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    /*******************
     * WISHLIST ITEMS
     *******************/
    $("#item-clear-btn").click(function(){
        clear_wishlist_item_form()
    })

    $("#wishlist-items-table").on("click", ".item-edit-btn", function(evnt){
        // make a call to the endpoint 
        // this isn't really efficient or necessary but for the purpose of explicitly testing 
        // the Read endpoint we include it
        const btn = $(evnt.target)
        const ids = btn.data("wishlist-and-item-id")
        const tokens = ids.split(":")

        $.ajax({
            method: "GET",
            url: `/wishlists/${tokens[0]}/items/${tokens[1]}`
        }).done(function(res){
            // populate wishlist item form with data from response
            $("#item_id").val(res.id)
            $("#item_wishlist_id").val(res.wishlist_id)
            $("#item_product_id").val(res.product_id)
            $("#item_product_name").val(res.product_name)
            $("#item_price").val(res.product_price)
            $("#item_quantity").val(res.quantity)
        })
    })

    // add a new item to the wishlist list
    $("#item-create-btn").click(function(){
        
        const wishlist_id = $("#item_wishlist_id").val()

        const post_data = {
            wishlist_id: $("#item_wishlist_id").val(),
            product_id: $("#item_product_id").val(),
            product_name: $("#item_product_name").val(),
            product_price: $("#item_price").val(),
            quantity: $("#item_quantity").val(),
            created_date: (new Date().toISOString()).slice(0, -1) //remove trailing Z which python doesn't like
        }

        $.ajax({
            method: "POST",
            url: `/wishlists/${wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(post_data)
        }).done(function(res){
            $("#item_id").val(res.id)
            flash_message("Successfully added item")
        })
    })

    // Delete an item from the list
    $("#wishlist-items-table").on("click", ".item-delete-btn", function(evnt){
        // make a call to the endpoint 
        const btn = $(evnt.target)
        const ids = btn.data("wishlist-and-item-id")
        const tokens = ids.split(":")

        $.ajax({
            method: "DELETE",
            url: `/wishlists/${tokens[0]}/items/${tokens[1]}`,
            contentType: "application/json",
            data: '',
        }).done(function(res, statusText, jqXHR){
            // Update visible list without changing success flash
            if (jqXHR.status === 204) {
                // Success - update visible list without changing success flash
                retrieveAndUpdateWishlist(tokens[0], false)
                    .then(() => {
                        flash_message("Successfully deleted item");
                    })
                    .catch((error) => {
                        console.log("Error updating wishlist:", error);
                        // Handle error if needed
                    });
            } else {
                // Handle other status codes if needed
                console.log(`Request failed with status: ${jqXHR.status}`);
            }
        })
    })

    // ****************************************
    // Update a Wishlist Item
    // ****************************************

    $("#item-update-btn").click(function () {

        let item_id = $("#item_id").val()
        let wishlist_id = $("#item_wishlist_id").val()
        let product_id = $("#item_product_id").val()
        let product_name = $("#item_product_name").val()
        let product_price = $("#item_price").val()
        let quantity = $("#item_quantity").val()

        let data = {
            "item_id": item_id,
            "wishlist_id": wishlist_id,
            "product_id": product_id,
            "product_name": product_name,
            "product_price": product_price,
            "quantity": quantity,
            "created_date": (new Date()).toISOString()
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/wishlists/${wishlist_id}/items/${item_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Successfully updated item")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
