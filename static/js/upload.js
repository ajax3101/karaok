document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    document.getElementById('progress').style.display = 'block';

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        window.location.href = `/result/${data.session_id}`;
    })
    .catch(err => {
        alert("Ошибка загрузки: " + err);
        document.getElementById('progress').style.display = 'none';
    });
});
