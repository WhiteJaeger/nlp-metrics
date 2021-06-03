function populateWithOutput(output) {
    const originalText = output.text;
    const wordToPOS = output.pos;
    $('#output-container').attr('class', 'container-md');
    $('#original-text').text(originalText);

    for (let wordPOSMap of wordToPOS) {
        const row = `<tr>
<td class="text-center">${wordPOSMap[0]}</td>
<td class="text-center">${wordPOSMap[1]}</td>
</tr>`
        $('#word-pos-table').append(row)
    }
}

function postData() {
    const inputForm = $('#input-text');
    const inputText = inputForm.val();

    inputForm.val('');
    $.blockUI();

    $.ajax({
        url: '/api/pos',
        method: 'POST',
        data: JSON.stringify({'text': inputText}),
        mimeType: 'application/json',
        processData: false,
        success: function (data) {
            populateWithOutput(JSON.parse(data));
            $('#submit-button').prop('disabled', true);
            $.unblockUI();
        }
    });
}

function toggleSubmitButton() {
    $('#submit-button').prop('disabled', $('#input-text').val() === '')
}

$('#submit-button').click(postData);
$('#input-text').keyup(toggleSubmitButton);
