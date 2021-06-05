function populateWithOutput(output) {
    const originalText = output.text;
    const pathToSentenceTree = output['syntax_tree_svg_path'];
    $('#output-container').attr('class', 'container-md');
    $('#original-text').text(originalText);
    $('#syntax-tree').attr('src', pathToSentenceTree)
}

function postData() {
    const inputForm = $('#input-text');
    const inputText = inputForm.val();

    inputForm.val('');
    $.blockUI();

    $.ajax({
        url: '/api/sentence-trees',
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
