function hideSentenceBoxes() {
    const el = document.getElementById('sentence-level');
    if (document.getElementById('text-type-select').value === 'corpus') {
        el.setAttribute('class', 'd-none');
    } else {
        el.setAttribute('class', 'form-control');
    }
}

document.getElementById('text-type-select').addEventListener('change', hideSentenceBoxes)
