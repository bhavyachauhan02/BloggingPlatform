document.addEventListener("DOMContentLoaded", function () {
    const API_BASE_URL = "http://127.0.0.1:5000"; // Replace this with your Flask server URL

    // Regular expressions for email and password validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

// User Registration Form
const registrationForm = document.getElementById("registrationForm");
registrationForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(registrationForm);
    const username = formData.get("username");
    const email = formData.get("email");
    const password = formData.get("password");

    // Email validation
    if (!emailRegex.test(email)) {
        alert("Invalid email address.");
        return;
    }

    // Password validation
    if (!passwordRegex.test(password)) {
        alert("Password must contain at least one uppercase letter, one lowercase letter, one special character, one number, and be at least 8 characters long.");
        return;
    }

    // Continue with registration if email and password validation passes
    const userData = {
        username: username,
        email: email,
        password: password
    };

    fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        registrationForm.reset();
    })
    .catch(error => console.error("Error:", error));
});

// User Login Form
const loginForm = document.getElementById("loginForm");
loginForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData(loginForm);
    const usernameOrEmail = formData.get("usernameOrEmail");
    const password = formData.get("password");

    // Email validation (assuming users can log in with email or username)
    if (!emailRegex.test(usernameOrEmail) && !usernameRegex.test(usernameOrEmail)) {
        alert("Invalid email or username.");
        return;
    }

    // Password validation
    if (!passwordRegex.test(password)) {
        alert("Invalid password format. Password must contain at least one uppercase letter, one lowercase letter, one special character, one number, and be at least 8 characters long.");
        return;
    }

    // Continue with login if email/username and password validation passes
    const userData = {
        usernameOrEmail: usernameOrEmail,
        password: password
    };

    fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loginForm.reset();
    })
    .catch(error => console.error("Error:", error));
});


    // Blog Post Creation Form
    const blogPostForm = document.getElementById("blogPostForm");
    blogPostForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(blogPostForm);
        const title = formData.get("title");
        const content = formData.get("content");

        // Basic title and content length validation
        if (title.length === 0 || content.length === 0) {
            alert("Title and content are required fields");
            return;
        }

        // Send blog post creation request to the server if validation passes
        const postData = {
            title: title,
            content: content
        };

        fetch(`${API_BASE_URL}/blog_posts`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            blogPostForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    // Blog Post Update Form
    const updateBlogForm = document.getElementById("updateBlogForm");
    updateBlogForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(updateBlogForm);
        const updateData = {
            title: formData.get("title"),
            content: formData.get("content")
        };
        const postId = formData.get("postId");

        fetch(`${API_BASE_URL}/blog_posts/${postId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            updateBlogForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    // Blog Post Deletion Form
    const deleteBlogForm = document.getElementById("deleteBlogForm");
    deleteBlogForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(deleteBlogForm);
        const postId = formData.get("postId");

        fetch(`${API_BASE_URL}/posts/${postId}`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            deleteBlogForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    // Comment Creation Form
    const commentForm = document.getElementById("commentForm");
    commentForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(commentForm);
        const commenterName = formData.get("commenterName");
        const commentText = formData.get("commentText");
        const postId = formData.get("postId");

        // Basic commenter name and comment text length validation
        if (commenterName.length === 0 || commentText.length === 0) {
            alert("Commenter name and comment text are required fields");
            return;
        }

        // Send comment creation request to the server if validation passes
        const commentData = {
            commenterName: commenterName,
            commentText: commentText,
            postId: postId
        };

        fetch(`${API_BASE_URL}/comments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(commentData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            commentForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    // Comment Update Form
    const updateCommentForm = document.getElementById("updateCommentForm");
    updateCommentForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(updateCommentForm);
        const updateData = {
            commenter_name: formData.get("commenterName"),
            comment_text: formData.get("commentText"),
            blog_post_id: formData.get("postId")
        };
        const commentId = formData.get("commentId");

        fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(updateData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            updateCommentForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    // Comment Deletion Form
    const deleteCommentForm = document.getElementById("deleteCommentForm");
    deleteCommentForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(deleteCommentForm);
        const commentId = formData.get("commentId");

        fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            deleteCommentForm.reset();
        })
        .catch(error => console.error("Error:", error));
    });

    /*
    // Fetch and Display Blog Posts
    fetch(`${API_BASE_URL}/blog_posts`)
        .then(response => response.json())
        .then(blogPosts => {
            const blogPostsList = document.getElementById("blogPostsList");
            blogPosts.forEach(post => {
                const listItem = document.createElement("li");
                listItem.textContent = `ID: ${post._id}, Title: ${post.title}, Content: ${post.content}`;
                blogPostsList.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error:", error));

    // Fetch and Display Comments
    fetch(`${API_BASE_URL}/comments`)
        .then(response => response.json())
        .then(comments => {
            const commentsList = document.getElementById("commentsList");
            comments.forEach(comment => {
                const listItem = document.createElement("li");
                listItem.textContent = `ID: ${comment._id}, Name: ${comment.commenter_name}, Text: ${comment.comment_text}, Post ID: ${comment.blog_post_id}`;
                commentsList.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error:", error));
        */

 // Function to fetch and display blogs

    const fetchBlogsButton = document.getElementById("fetchBlogsButton");
    const blogPostsList = document.getElementById("blogPostsList");

    fetchBlogsButton.addEventListener("click", function () {
        // Fetch blogs from the server
        fetch("/blog_posts")
            .then(response => response.json())
            .then(blogPosts => {
                // Clear existing content
                blogPostsList.innerHTML = "";
                // Display fetched blogs
                blogPosts.forEach(post => {
                    const listItem = document.createElement("li");
                    listItem.textContent = `ID: ${post._id}, Title: ${post.title}, Content: ${post.content}`;
                    blogPostsList.appendChild(listItem);
                });
            })
            .catch(error => console.error("Error fetching blogs:", error));
    });


    // Function to fetch and display comments
const fetchCommentsButton = document.getElementById("fetchCommentsButton");
const commentsList = document.getElementById("commentsList");

fetchCommentsButton.addEventListener("click", function () {
    // Fetch comments from the server
    fetch("/comments")
        .then(response => response.json())
        .then(comments => {
            // Clear existing content
            commentsList.innerHTML = "";
            // Display fetched comments
            comments.forEach(comment => {
                const listItem = document.createElement("li");
                listItem.textContent = `ID: ${comment._id}, Name: ${comment.commenter_name}, Text: ${comment.comment_text}, Post ID: ${comment.blog_post_id}`;
                commentsList.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error fetching comments:", error));
});

});
