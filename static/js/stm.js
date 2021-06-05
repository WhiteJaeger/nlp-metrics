function populateWithOutputSentenceLevel(output) {
    const {
        reference,
        hypothesis,
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

function populateWithOutputCorpusLevel(output) {
    const {
        score,
        depth,
        isGenreEnabled,
        isSentimentEnabled,
        per_sentence_summary: perSentenceSummary,
        corpora_genres: corporaGenres
    } = output;
    if (perSentenceSummary) {
        $('#per-sentence-summary').removeClass('d-none')
        for (let summary of perSentenceSummary) {
            let row = `
<div class="content-section">
    <div class="row">
        <div class="col border per-sentence-info"><strong>Reference sentence</strong>: ${summary.reference}</div>
        <div class="col border per-sentence-info"><strong>Hypothesis sentence</strong>: ${summary.hypothesis}</div>
    </div>`;
            if (Number(isSentimentEnabled)) {
                row = `${row} <div class="row">
                                <div class="col border per-sentence-info"><strong>Reference
                                    sentiment</strong>: ${summary.sentiment_ref}</div>
                                <div class="col border per-sentence-info"><strong>Hypothesis
                                    sentiment</strong>: ${summary.sentiment_hyp}</div>
                            </div>`
            }
            if (Number(isGenreEnabled)) {
                row = `${row} <div class="row">
                                <div class="col border per-sentence-info"><strong>Reference
                                    genre</strong>: ${summary.genre_ref}</div>
                                <div class="col border per-sentence-info"><strong>Hypothesis
                                    genre</strong>: ${summary.genre_hyp}</div>
                            </div>`
            }
            row = `${row} <p class="stm-score text-center"><strong>STM Score</strong>: ${summary.score} out of
                            1.0</p>`
            row = `${row} </div>`
            $('#per-sentence-summary').append(row);
        }
    }
    // TODO: check for sentence-level container
    $('#output-container').removeClass('d-none');
    $('#analyzers').removeClass('d-none')
    $('#genre-analysis-output').removeClass('d-none')

    $('#metric-score').text(score);
    $('#depth-value').text(depth);
    const sentimentAnalyzerEnabled = Number(isSentimentEnabled) ? 'Yes' : 'No';
    $('#sentiment-analyzer-enabled').text(sentimentAnalyzerEnabled)

    if (Number(isGenreEnabled)) {
        $('#genre-analyzer-enabled').text('Yes')
        $('#corpora-genre').removeClass('d-none')
        $('#hypothesis-corpora-genre').text(corporaGenres.hypothesis)
        $('#reference-corpora-genre').text(corporaGenres.reference)
    } else {
        $('#genre-analyzer-enabled').text('No')
    }
}

function postSentenceLevel() {

    $.blockUI();

    const formPrefix = '#sentence-level';

    const inputFormReference = $(`${formPrefix} #input-text-reference`);
    const inputTextReference = inputFormReference.val();

    const inputFormHypothesis = $(`${formPrefix} #input-text-hypothesis`);
    const inputTextHypothesis = inputFormHypothesis.val();

    const depth = $(`${formPrefix} select[name=depth] option`).filter(':selected').val();

    const sentimentEl = $(`${formPrefix} #sentiment-sentence`);
    const isSentimentEnabled = sentimentEl.is(':checked') ? '1' : '0';

    const contractionsEl = $(`${formPrefix} #contractions`);
    const specCharsEl = $(`${formPrefix} #spec-chars`);
    const lowercaseEl = $(`${formPrefix} #lowercase`);

    const preprocessing = {
        'contractions': contractionsEl.is(':checked') ? 1 : 0,
        'spec-chars': specCharsEl.is(':checked') ? 1 : 0,
        'lowercase': lowercaseEl.is(':checked') ? 1 : 0
    }

    // Data
    const data = new FormData();
    data.append('type', 'sentence-level')
    data.append('reference', inputTextReference);
    data.append('hypothesis', inputTextHypothesis);
    data.append('depth', depth);
    data.append('preprocessing', JSON.stringify(preprocessing));
    data.append('isSentimentEnabled', isSentimentEnabled);

    $.ajax({
        url: '/api/stm',
        method: 'POST',
        data: data,
        mimeType: 'application/json',
        processData: false,
        contentType: false,
        success: function (data) {
            inputFormReference.val('');
            inputFormHypothesis.val('');
            [contractionsEl, specCharsEl, lowercaseEl, sentimentEl].forEach(function (el) {
                el.prop('checked', false)
            });
            $(`${formPrefix} #depth`).val('').change();
            removeOldOutput();
            $.ajaxStop(function () {
                populateWithOutputSentenceLevel(JSON.parse(data));
                $('#submit-button-sentence').prop('disabled', true);
                $.unblockUI();
            })
        }
    });
}

function postCorpusLevel() {

    $.blockUI();

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

    // Data
    const data = new FormData();
    data.append('type', 'corpus-level')
    data.append('hypothesis', $('#hypotheses-upload')[0].files[0], 'hypothesis.txt')
    data.append('reference', $('#references-upload')[0].files[0], 'reference.txt')
    data.append('preprocessing', JSON.stringify(preprocessing))
    data.append('isSentimentEnabled', isSentimentEnabled);
    data.append('isGenreEnabled', isGenreEnabled);
    data.append('depth', depth);

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
            $('#hypotheses-upload').val('')
            $('#references-upload').val('')
            removeOldOutput()
            $.ajaxStop(function () {
                populateWithOutputCorpusLevel(JSON.parse(data));
                $('#submit-button-corpus').prop('disabled', true);
                $.unblockUI();
            })
        }
    });
}

function postData() {
    const type = $('select[name=text-type] option').filter(':selected').val();
    if (type === 'sentence') {
        postSentenceLevel();
    } else if (type === 'corpus') {
        postCorpusLevel();
    }
}


function toggleSubmitButton() {
    const type = $('select[name=text-type] option').filter(':selected').val();
    if (type === 'sentence') {
        const isRefEmpty = $('#input-text-reference').val() === '';
        const isHypEmpty = $('#input-text-hypothesis').val() === '';
        const isDepthSelected = $('#sentence-level select[name=depth] option').filter(':selected').val() !== '';
        $('#submit-button-sentence').prop('disabled', isRefEmpty || isHypEmpty || !isDepthSelected)
    } else if (type === 'corpus') {
        const isRefEmpty = $('#references-upload').get(0).files.length === 0;
        const isHypEmpty = $('#hypotheses-upload').get(0).files.length === 0;
        const isDepthSelected = $('#corpus-level select[name=depth] option').filter(':selected').val() !== '';
        $('#submit-button-corpus').prop('disabled', isRefEmpty || isHypEmpty || !isDepthSelected)
    }
}


function removeOldOutput() {
    // Reload the output part of the page
    $('#output-container-outer').load($SCRIPT_ROOT + 'stm #output-container')
}

// TODO: extract common parts in HTML
$(document).ready(function () {
    // $(document).ajaxStart(removeOldOutput);
    $('#submit-button-corpus').click(postData);
    $('#submit-button-sentence').click(postData);

    // Sentence level check
    $('#input-text-hypothesis').keyup(toggleSubmitButton);
    $('#input-text-reference').keyup(toggleSubmitButton);
    $('#sentence-level #depth').on('change', toggleSubmitButton);

    // Corpus level check
    $('#references-upload').on('change', toggleSubmitButton)
    $('#hypotheses-upload').on('change', toggleSubmitButton)
    $('#corpus-level #depth').on('change', toggleSubmitButton);

})


// TODO: rewrite
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
