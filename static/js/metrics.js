function toggleInputForms() {

    const sentenceLevelFormClass = 'form-control';
    const corpusLevelFormClass = 'content-section';

    const sentenceLevelForm = document.getElementById('sentence-level');
    const corpusLevelForm = document.getElementById('corpus-level');

    if (document.getElementById('text-type-select').value === 'corpus') {
        sentenceLevelForm.setAttribute('class', 'd-none');
        corpusLevelForm.setAttribute('class', corpusLevelFormClass)
    } else {
        corpusLevelForm.setAttribute('class', 'd-none');
        sentenceLevelForm.setAttribute('class', sentenceLevelFormClass)
    }
}

document.getElementById('text-type-select').addEventListener('change', toggleInputForms)
