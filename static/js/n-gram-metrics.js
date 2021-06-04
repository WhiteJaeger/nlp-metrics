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
    const inputFormReference = $('#input-text-reference');
    const inputTextReference = inputFormReference.val();

    const inputFormHypothesis = $('#input-text-hypothesis');
    const inputTextHypothesis = inputFormHypothesis.val();

    const metricNameForm = $('#metric-select');
    const metricName = $('select[name=metric] option').filter(':selected').val()

    const contractionsEl = $('#contractions');
    const specCharsEl = $('#spec-chars');
    const lowercaseEl = $('#lowercase');

    inputFormReference.val('');
    inputFormHypothesis.val('');
    metricNameForm.val('').change();
    [contractionsEl, specCharsEl, lowercaseEl].forEach(function (el) {
        el.prop('checked', false)
    })
    $.blockUI();

    const data = {
        'reference': inputTextReference,
        'hypothesis': inputTextHypothesis,
        'metric': metricName
    }

    $.ajax({
        url: '/api/n-gram-metrics',
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
    const isRefEmpty = $('#input-text-reference').val() === '';
    const isHypEmpty = $('#input-text-hypothesis').val() === '';
    const isMetricSelected = $('select[name=metric] option').filter(':selected').val() !== '';
    $('#submit-button').prop('disabled', isRefEmpty || isHypEmpty || !isMetricSelected)
}

$('#submit-button').click(postData);
$('#input-text-hypothesis').keyup(toggleSubmitButton);
$('#input-text-reference').keyup(toggleSubmitButton);
$('#metric-select').on('change', toggleSubmitButton);
