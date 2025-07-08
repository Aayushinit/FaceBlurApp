document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const resultSection = document.getElementById('resultSection');
    const resultImage = document.getElementById('resultImage');
    const downloadLink = document.getElementById('downloadLink');

    // Drag and drop events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, unhighlight, false);
    });

    dropzone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    function highlight(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('border-indigo-500', 'bg-indigo-50');
    }

    function unhighlight(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('border-indigo-500', 'bg-indigo-50');
    }

    function handleDrop(e) {
        e.preventDefault();
        unhighlight(e);
        const file = e.dataTransfer.files[0];
        handleFile(file);
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        handleFile(file);
    }

    function handleFile(file) {
        if (!file.type.match('image.*')) {
            alert('Please select a valid image file (JPEG, PNG)');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert('File exceeds 10MB limit');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error processing image');
            }
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            resultImage.src = url;
            downloadLink.href = url; // Set the download link
            downloadLink.classList.remove('hidden'); // Show the download link
            resultSection.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
        });
    }
});
