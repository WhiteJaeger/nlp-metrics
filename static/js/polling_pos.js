function setValue() {
    $('#file').attr('value', 'randomString');
}

/**
 * Simple long polling client based on JQuery
 */

/**
 * Request an update to the server and once it has answered, then update
 * the content and request again.
 * The server is supposed to response when a change has been made on data.
 */
function update() {
    $.ajax({
        url: '/data-update-pos',
        success: function (data) {
            $('#dateChange').text(data.date);
            $('#content').text(data.content);
            update();
        },
        timeout: 500000 // If timeout is reached run again
    });
}

/**
 * Perform first data request. After taking this data, just query the
 * server and refresh when answered (via update call).
 */
function load() {
    $.ajax({
        url: '/data-pos',
        success: function (data) {
            $('#content').text(data.content);
            update();
        }
    });
}

function testPOST() {
    console.log(123);
    $.ajax({
        url: '/data-update-pos',
        method: 'POST',
        data: JSON.stringify({'abc': 123, 'dcv': 435}),
        mimeType: 'application/json',
        processData: false
    });
}


$(document).ready(function () {
    setValue();
    testPOST();
    load();
})
