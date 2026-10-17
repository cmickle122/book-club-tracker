document.addEventListener('DOMContentLoaded', function() {
    console.log("Page-Turner App JavaScript initialized.");

    const spoilerLinks = document.querySelectorAll('.spoiler-thread-link');
    spoilerLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const userProgress = parseInt(this.getAttribute('data-user-progress') || '0');
            const targetChapter = parseInt(this.getAttribute('data-chapter-num') || '0');

            if (targetChapter > userProgress) {
                const confirmAccess = confirm(`⚠️ SPOILER WARNING!\n\nYour current progress is Chapter ${userProgress}, but this thread discusses Chapter ${targetChapter}.\n\nAre you sure you want to view this thread?`);
                if (!confirmAccess) {
                    e.preventDefault();
                }
            }
        });
    });

    // ==============================================================================
    // WRITE YOUR TEAM'S CUSTOM JAVASCRIPT HERE
    // ==============================================================================
    // Write your code here:

    // Example custom event handling

    // To here.
});
