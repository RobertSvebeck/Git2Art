document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('artForm');
    const generateBtn = document.getElementById('generateBtn');
    const status = document.getElementById('status');
    const resultSection = document.getElementById('resultSection');
    const artworkImage = document.getElementById('artworkImage');
    const repoName = document.getElementById('repoName');
    const downloadBtn = document.getElementById('downloadBtn');
    const newArtBtn = document.getElementById('newArtBtn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const githubUrl = document.getElementById('githubUrl').value.trim();
        const forceRegenerate = document.getElementById('forceRegenerate').checked;

        // Clear the input box as soon as processing starts
        document.getElementById('githubUrl').value = '';

        showStatus('Generating artwork... This may take a minute.', 'info');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="spinner"></span>Generating...';
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    github_url: githubUrl,
                    force_regenerate: forceRegenerate
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate artwork');
            }

            const cachedMsg = data.cached ? ' (from cache)' : '';
            showStatus(`Artwork generated successfully!${cachedMsg}`, 'success');

            repoName.textContent = data.repo_name;
            artworkImage.src = data.image_url;

            const filename = data.image_url.split('/').pop();
            downloadBtn.href = `/download/${filename}`;

            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Art';
        }
    });

    newArtBtn.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        document.getElementById('githubUrl').value = '';
        document.getElementById('forceRegenerate').checked = false;
        document.getElementById('githubUrl').focus();
        hideStatus();
    });

    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status ${type}`;
        status.classList.remove('hidden');
    }

    function hideStatus() {
        status.classList.add('hidden');
    }
});
