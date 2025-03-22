// Dynamic variable assignments will be passed from the template
function initBlog(pageId) {
    // Copy link button
    const copyButtons = document.querySelectorAll('button[data-action="copy-link"]');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const icon = button.querySelector('i');
            const originalClass = icon.className;
            navigator.clipboard.writeText(window.location.href);
            icon.className = 'fas fa-check text-xl';
            setTimeout(() => {
                icon.className = originalClass;
            }, 2000);
        });
    });

    // Comments functionality
    const commentForm = document.getElementById('comment-form');
    const commentsContainer = document.getElementById('comments');

    async function loadComments() {
        try {
            const response = await fetch(`/api/comments?page_id=${pageId}`);
            const data = await response.json();
            renderComments(data.comments);
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    function renderComments(comments) {
        if (!comments || !comments.length) {
            commentsContainer.innerHTML = '<p class="text-gray-500">No comments yet. Be the first to comment!</p>';
            return;
        }

        commentsContainer.innerHTML = comments.map(comment => `
            <div class="flex space-x-3 mb-6">
                <div class="flex-shrink-0">
                    <img class="h-10 w-10 rounded-full" src="${comment.author.avatar}" alt="${comment.author.name}">
                </div>
                <div class="flex-1 space-y-1">
                    <div class="flex items-center justify-between">
                        <h3 class="text-sm font-medium text-gray-900">${comment.author.name}</h3>
                        <time class="text-sm text-gray-500">${new Date(comment.created_at).toLocaleDateString()}</time>
                    </div>
                    <p class="text-sm text-gray-500">${comment.content}</p>
                </div>
            </div>
        `).join('');
    }

    if (commentForm) {
        commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitButton = commentForm.querySelector('button[type="submit"]');
            const comment = commentForm.querySelector('#comment').value;

            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Posting...';

            try {
                const response = await fetch('/api/comments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        page_id: pageId,
                        content: comment
                    })
                });

                if (response.ok) {
                    commentForm.reset();
                    loadComments();
                }
            } catch (error) {
                console.error('Error posting comment:', error);
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Post Comment';
            }
        });
    }

    // Load initial comments
    if (commentsContainer) {
        loadComments();
    }
}
