document.addEventListener('DOMContentLoaded', function() {
    console.log("BookCircle App JavaScript initialized.");

    const spoilerLinks = document.querySelectorAll('.spoiler-thread-link');
    spoilerLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const userProgress = parseInt(this.getAttribute('data-user-progress') || '0');
            const targetChapter = parseInt(this.getAttribute('data-chapter-num') || '0');

            if (targetChapter > userProgress) {
                const chapterLabel = (n) => n === 0 ? 'Prologue' : `Chapter ${n}`;
                const progressText = userProgress < 0 ? 'Not Started' : chapterLabel(userProgress);

                const confirmAccess = confirm(
                    `⚠️ SPOILER WARNING!\n\nYour current progress is ${progressText}, but this thread discusses ${chapterLabel(targetChapter)}.\n\nClick OK to proceed to the discussion. Click Cancel to go back.`
                );
                if (!confirmAccess) {
                    e.preventDefault();
                }
            }
        });
    });

    const privacySelect = document.getElementById('privacySelect');
    const passcodeContainer = document.getElementById('passcodeContainer');
    const passcodeField = document.getElementById('passcodeField');

    if (privacySelect && passcodeContainer && passcodeField) {
        privacySelect.addEventListener('change', function() {
            if (this.value === '1') {
                passcodeContainer.style.display = 'block';
                passcodeField.setAttribute('required', 'required');
            } else {
                passcodeContainer.style.display = 'none';
                passcodeField.removeAttribute('required');
            }
        });
    }
});