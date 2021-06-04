function populateWithOutput(output) {
    const {reference, hypothesis, metric, score} = output;

    $('#output-container').removeClass('d-none');
    $('#hypothesis-sentence').text(hypothesis);
    $('#reference-sentence').text(reference);
    $('#metric-name').text(metric);
    $('#metric-score').text(score);
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

    const preprocessing = {
        'contractions': contractionsEl.is(':checked') ? 1 : 0,
        'spec-chars': specCharsEl.is(':checked') ? 1 : 0,
        'lowercase': lowercaseEl.is(':checked') ? 1 : 0
    }

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
        'metric': metricName,
        'preprocessing': preprocessing
    }

    $.ajax({
        url: '/api/n-gram-metrics',
        method: 'POST',
        data: JSON.stringify(data),
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

$(document).ready(function () {
    $('#submit-button').click(postData);
    $('#input-text-hypothesis').keyup(toggleSubmitButton);
    $('#input-text-reference').keyup(toggleSubmitButton);
    $('#metric-select').on('change', toggleSubmitButton);
})
