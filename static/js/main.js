// Mark lesson as complete
const completeBtn = document.getElementById('complete-btn');
if (completeBtn) {
    completeBtn.addEventListener('click', async () => {
        const lessonId = completeBtn.dataset.lesson;
        const courseId = completeBtn.dataset.course;
        completeBtn.disabled = true;
        completeBtn.textContent = 'Saving...';

        const res = await fetch(`/complete-lesson/${lessonId}`, { method: 'POST' });
        const data = await res.json();

        if (data.progress !== undefined) {
            // Update sidebar progress bar
            const bars = document.querySelectorAll('.progress-bar');
            bars.forEach(b => b.style.width = data.progress + '%');
            const label = document.getElementById('progress-label');
            if (label) label.textContent = data.progress + '% complete';

            completeBtn.textContent = '✅ Completed!';
            completeBtn.classList.remove('btn-primary');
            completeBtn.classList.add('btn-success');

            if (data.completed) {
                setTimeout(() => {
                    window.location.href = `/certificate/${courseId}`;
                }, 1500);
            }
        }
    });
}

// Auto-dismiss flash messages
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.transition = 'opacity .5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 4000);
