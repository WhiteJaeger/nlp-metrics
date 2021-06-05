function populateWithOutputSentenceLevel(output) {
    const {
        reference,
        hypothesis,
        metric,
        score,
        depth,
        isSentimentEnabled,
        reference_syntax_tree_path: referenceSyntaxTreePath,
        hypothesis_syntax_tree_path: hypothesisSyntaxTreePath
    } = output;
    // TODO: check for corpus-level container
    $('#output-container').removeClass('d-none');
    $('#sentence-level-output').removeClass('d-none');
    $('#analyzers').removeClass('d-none')

    $('#hypothesis-sentence').text(hypothesis);
    $('#reference-sentence').text(reference);
    $('#metric-score').text(score);
    $('#depth-value').text(depth);
    $('#hypothesis-syntax-tree').attr('src', hypothesisSyntaxTreePath)
    $('#reference-syntax-tree').attr('src', referenceSyntaxTreePath)
    const sentimentAnalyzerEnabled = Number(isSentimentEnabled) ? 'Yes' : 'No';
    $('#sentiment-analyzer-enabled').text(sentimentAnalyzerEnabled)
}

function postSentenceLevel() {
    const formPrefix = '#sentence-level';

    const inputFormReference = $(`${formPrefix} #input-text-reference`);
    const inputTextReference = inputFormReference.val();

    const inputFormHypothesis = $(`${formPrefix} #input-text-hypothesis`);
    const inputTextHypothesis = inputFormHypothesis.val();

    const depth = $(`${formPrefix} select[name=depth] option`).filter(':selected').val();

    const sentimentEl = $(`${formPrefix} #sentiment-sentence`);
    const isSentimentEnabled = sentimentEl.is(':checked') ? 1 : 0;

    const contractionsEl = $(`${formPrefix} #contractions`);
    const specCharsEl = $(`${formPrefix} #spec-chars`);
    const lowercaseEl = $(`${formPrefix} #lowercase`);

    const preprocessing = {
        'contractions': contractionsEl.is(':checked') ? 1 : 0,
        'spec-chars': specCharsEl.is(':checked') ? 1 : 0,
        'lowercase': lowercaseEl.is(':checked') ? 1 : 0
    }

    const data = {
        'reference': inputTextReference,
        'hypothesis': inputTextHypothesis,
        'depth': depth,
        'preprocessing': preprocessing,
        'isSentimentEnabled': isSentimentEnabled
    }

    $.blockUI();

    $.ajax({
        url: '/api/stm',
        method: 'POST',
        data: JSON.stringify(data),
        mimeType: 'application/json',
        processData: false,
        success: function (data) {
            inputFormReference.val('');
            inputFormHypothesis.val('');
            [contractionsEl, specCharsEl, lowercaseEl, sentimentEl].forEach(function (el) {
                el.prop('checked', false)
            });
            $(`${formPrefix} #depth`).val('').change();
            populateWithOutputSentenceLevel(JSON.parse(data));
            $('#submit-button').prop('disabled', true);
            $.unblockUI();
        }
    });
}

function postCorpusLevel() {
    const formPrefix = '#corpus-level';

    const contractionsEl = $(`${formPrefix} #contractions`);
    const specCharsEl = $(`${formPrefix} #spec-chars`);
    const lowercaseEl = $(`${formPrefix} #lowercase`);

    const depth = $(`${formPrefix} select[name=depth] option`).filter(':selected').val();

    const sentimentEl = $(`${formPrefix} #sentiment`);
    const isSentimentEnabled = sentimentEl.is(':checked') ? '1' : '0';

    const genreEl = $(`${formPrefix} #genre`);
    const isGenreEnabled = genreEl.is(':checked') ? '1' : '0';
    const preprocessing = {
        'contractions': contractionsEl.is(':checked') ? 1 : 0,
        'spec-chars': specCharsEl.is(':checked') ? 1 : 0,
        'lowercase': lowercaseEl.is(':checked') ? 1 : 0
    }

    // Files
    const data = new FormData();
    data.append('hypothesis', $('#hypotheses-upload')[0].files[0], 'hypothesis.txt')
    data.append('reference', $('#references-upload')[0].files[0], 'reference.txt')
    data.append('preprocessing', JSON.stringify(preprocessing))
    data.append('isSentimentEnabled', isSentimentEnabled);
    data.append('isGenreEnabled', isGenreEnabled);
    data.append('depth', depth);

    $.blockUI();

    $.ajax({
        url: '/api/stm',
        method: 'POST',
        data: data,
        mimeType: 'application/json',
        processData: false,
        contentType: false,
        success: function (data) {
            [contractionsEl, specCharsEl, lowercaseEl, sentimentEl, genreEl].forEach(function (el) {
                el.prop('checked', false)
            });
            $(`${formPrefix} #depth`).val('').change();
            // populateWithOutputSentenceLevel(JSON.parse(data));
            $('#submit-button').prop('disabled', true);
            $.unblockUI();
        }
    });
}

function postData() {

    const type = $('select[name=text-type] option').filter(':selected').val();
    console.log(type);
    if (type === 'sentence') {
        postSentenceLevel();
    } else if (type === 'corpus') {
        postCorpusLevel();
    }

    // TODO: RETURN ELEMENTS TO THEIR STATE

    // [contractionsEl, specCharsEl, lowercaseEl].forEach(function (el) {
    //     el.prop('checked', false)
    // })
    //
    //
    // inputFormReference.val('');
    // inputFormHypothesis.val('');
    // $('#text-type-select').val('').change();

    // $.blockUI();
    //
    // const data = {
    //     'reference': inputTextReference,
    //     'hypothesis': inputTextHypothesis,
    //     'metric': metricName,
    //     'preprocessing': preprocessing
    // }
    //
    // $.ajax({
    //     url: '/api/n-gram-metrics',
    //     method: 'POST',
    //     data: JSON.stringify(data),
    //     mimeType: 'application/json',
    //     processData: false,
    //     success: function (data) {
    //         populateWithOutput(JSON.parse(data));
    //         $('#submit-button').prop('disabled', true);
    //         $.unblockUI();
    //     }
    // });
}

function toggleSubmitButton() {
    const isRefEmpty = $('#input-text-reference').val() === '';
    const isHypEmpty = $('#input-text-hypothesis').val() === '';
    const isMetricSelected = $('select[name=metric] option').filter(':selected').val() !== '';
    $('#submit-button').prop('disabled', isRefEmpty || isHypEmpty || !isMetricSelected)
}

// TODO: DIFFERENT BUTTONS
$(document).ready(function () {
    $('#corpus-level #submit-button').click(postData);
    // $('#input-text-hypothesis').keyup(toggleSubmitButton);
    // $('#input-text-reference').keyup(toggleSubmitButton);
    // $('#metric-select').on('change', toggleSubmitButton);
})




































function toggleInputForms() {

    const sentenceLevelFormClass = 'form-control';
    const corpusLevelFormClass = 'form-control';

    const sentenceLevelForm = document.getElementById('sentence-level');
    const corpusLevelForm = document.getElementById('corpus-level');

    if (document.getElementById('text-type-select').value === 'corpus') {
        sentenceLevelForm.setAttribute('class', 'd-none');
        corpusLevelForm.setAttribute('class', corpusLevelFormClass);

        document.getElementById('file-structure').setAttribute('class', 'content-section');
    } else {
        corpusLevelForm.setAttribute('class', 'd-none');
        sentenceLevelForm.setAttribute('class', sentenceLevelFormClass);
        document.getElementById('file-structure').setAttribute('class', 'd-none');
    }

    if (!!document.getElementById('output-info')) {
        document.getElementById('output-info').setAttribute('class', 'd-none');
    }

    if (!!document.getElementById('per-sentence-summary')) {
        document.getElementById('per-sentence-summary').setAttribute('class', 'd-none');
    }
}

document.getElementById('text-type-select').addEventListener('change', toggleInputForms)
