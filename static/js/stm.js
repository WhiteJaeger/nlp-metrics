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

function extractCommonParameters() {
    // Preprocessing
    const contractionsEl = $(`#contractions`);
    const specCharsEl = $(`#spec-chars`);
    const lowercaseEl = $(`#lowercase`);

    const preprocessing = {
        'contractions': contractionsEl.is(':checked') ? 1 : 0,
        'spec-chars': specCharsEl.is(':checked') ? 1 : 0,
        'lowercase': lowercaseEl.is(':checked') ? 1 : 0
    }

    // Depth
    const depth = $(`select[name=depth] option`).filter(':selected').val();

    return {
        'preprocessing': preprocessing,
        'depth': depth
    }
}

function returnCommonElementsToOriginalState() {
    // Preprocessing
    const contractionsEl = $(`#contractions`);
    const specCharsEl = $(`#spec-chars`);
    const lowercaseEl = $(`#lowercase`);
    [contractionsEl, specCharsEl, lowercaseEl].forEach(function (el) {
        el.prop('checked', false)
    });

    // Depth
    $(`#depth`).val('').change();
}

function postSentenceLevel() {

    $.blockUI();

    const inputFormReference = $(`#input-text-reference`);
    const inputTextReference = inputFormReference.val();

    const inputFormHypothesis = $(`#input-text-hypothesis`);
    const inputTextHypothesis = inputFormHypothesis.val();

    const sentimentEl = $(`#sentiment-sentence`);
    const isSentimentEnabled = sentimentEl.is(':checked') ? '1' : '0';

    const {preprocessing, depth} = extractCommonParameters()

    // Data
    const data = new FormData();
    data.append('type', 'sentence-level')
    data.append('reference', inputTextReference);
    data.append('hypothesis', inputTextHypothesis);
    data.append('depth', depth);
    data.append('preprocessing', JSON.stringify(preprocessing));
    data.append('isSentimentEnabled', isSentimentEnabled);

    $.when(removeOldOutput()).done(function () {
        $.ajax({
            url: '/api/stm',
            method: 'POST',
            data: data,
            mimeType: 'application/json',
            processData: false,
            contentType: false,
            success: function (data) {
                returnCommonElementsToOriginalState();
                inputFormReference.val('');
                inputFormHypothesis.val('');
                sentimentEl.prop('checked', false);
                $('#submit-button-sentence').prop('disabled', true);

                populateWithOutputSentenceLevel(JSON.parse(data));
            },
            complete: function () {
                $.unblockUI();
            }
        });
    })
}

function postCorpusLevel() {

    $.blockUI();

    const sentimentEl = $(`#sentiment-corpus`);
    const isSentimentEnabled = sentimentEl.is(':checked') ? '1' : '0';

    const genreEl = $(`#genre`);
    const isGenreEnabled = genreEl.is(':checked') ? '1' : '0';

    const {preprocessing, depth} = extractCommonParameters()

    // Data
    const data = new FormData();
    data.append('type', 'corpus-level')
    data.append('hypothesis', $('#hypotheses-upload')[0].files[0], 'hypothesis.txt')
    data.append('reference', $('#references-upload')[0].files[0], 'reference.txt')
    data.append('preprocessing', JSON.stringify(preprocessing))
    data.append('isSentimentEnabled', isSentimentEnabled);
    data.append('isGenreEnabled', isGenreEnabled);
    data.append('depth', depth);

    $.when(removeOldOutput()).done(function () {
        $.ajax({
            url: '/api/stm',
            method: 'POST',
            data: data,
            mimeType: 'application/json',
            processData: false,
            contentType: false,
            success: function (data) {
                returnCommonElementsToOriginalState();
                [sentimentEl, genreEl].forEach(function (el) {
                    el.prop('checked', false)
                });
                $('#hypotheses-upload').val('')
                $('#references-upload').val('')
                $('#submit-button-corpus').prop('disabled', true);

                populateWithOutputCorpusLevel(JSON.parse(data));

                // Use submit button as the top el so that the header does not cover the results
                $(window).scrollTop($('#submit-button-corpus').offset().top);
            },
            complete: function () {
                $.unblockUI();
            }
        });
    })
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
        const isDepthSelected = $('select[name=depth] option').filter(':selected').val() !== '';
        $('#submit-button-sentence').prop('disabled', isRefEmpty || isHypEmpty || !isDepthSelected)
    } else if (type === 'corpus') {
        const isRefEmpty = $('#references-upload').get(0).files.length === 0;
        const isHypEmpty = $('#hypotheses-upload').get(0).files.length === 0;
        const isDepthSelected = $('select[name=depth] option').filter(':selected').val() !== '';
        $('#submit-button-corpus').prop('disabled', isRefEmpty || isHypEmpty || !isDepthSelected)
    }
}


function removeOldOutput() {
    // Reload the output part of the page
    $('#output-container-outer').load($SCRIPT_ROOT + 'stm #output-container');
    return true;
}

function toggleInputForms() {

    const sentenceLevelForm = $('#sentence-level');
    const corpusLevelForm = $('#corpus-level');
    const commonPartsForm = $('#common');

    commonPartsForm.removeClass('d-none');

    if ($('#text-type-select').val() === 'corpus') {
        sentenceLevelForm.addClass('d-none');
        corpusLevelForm.removeClass('d-none');

        $('#file-structure').removeClass('d-none');
    } else {
        corpusLevelForm.addClass('d-none');
        sentenceLevelForm.removeClass('d-none');
        $('#file-structure').addClass('d-none');
    }
}

$(document).ready(function () {
    $('#submit-button-corpus').click(postData);
    $('#submit-button-sentence').click(postData);

    $('#depth').on('change', toggleSubmitButton);

    // Sentence level check
    $('#input-text-hypothesis').keyup(toggleSubmitButton);
    $('#input-text-reference').keyup(toggleSubmitButton);

    // Corpus level check
    $('#references-upload').on('change', toggleSubmitButton)
    $('#hypotheses-upload').on('change', toggleSubmitButton)

    $('#text-type-select').on('change', toggleInputForms)
})
