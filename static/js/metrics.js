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
}

document.getElementById('text-type-select').addEventListener('change', toggleInputForms)
