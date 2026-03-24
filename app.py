from flask import Flask, render_template_string, request, redirect, url_for
import requests
import json
import threading


# Local session-based storage (simulating a database)
local_posts = []
local_comments = []
comment_id_counter = 501 # jsonplaceholder comments go up to 500

# Cache dictionary to store API data
api_cache = {
    'posts': [],
    'users': [],
    'comments': []
}

def preload_data():
    try:
        api_cache['posts'] = requests.get('https://jsonplaceholder.typicode.com/posts').json()
        api_cache['users'] = requests.get('https://jsonplaceholder.typicode.com/users').json()
        api_cache['comments'] = requests.get('https://jsonplaceholder.typicode.com/comments').json()
        print("API data preloaded successfully for fast access.")
    except Exception as e:
        print(f"Failed to preload API data: {e}")

# Start preloading in a background thread so app starts instantly
threading.Thread(target=preload_data, daemon=True).start()

app = Flask(__name__)

# HTML template for posts dashboard
POSTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Posts | Editorial</title>
    <!-- Premium Typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #fcf9aa;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --accent-color: #0056b3;
            --border-color: #eeeeee;
            --card-bg: #ffffff;
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Inter', sans-serif;
            --max-width: 800px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 60px 20px;
        }

        .container {
            max-width: var(--max-width);
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 80px;
        }

        h1 {
            font-family: var(--font-serif);
            font-size: 3.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin-bottom: 10px;
            color: var(--text-main);
        }

        .subtitle {
            font-size: 1.1rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
        }

        .posts-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 60px;
        }

        .post-card {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 40px;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            text-decoration: none;
            color: inherit;
            display: block;
            opacity: 0;
            animation: fadeInUp 0.8s ease forwards;
        }

        .post-card:hover {
            opacity: 0.9;
            transform: translateY(-4px);
        }

        .post-img-container {
            width: 100%;
            height: 450px;
            overflow: hidden;
            border-radius: 4px;
            margin-bottom: 25px;
            background-color: #f0f0f0;
        }

        .post-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.8s cubic-bezier(0.165, 0.84, 0.44, 1);
        }

        .post-card:hover .post-img {
            transform: scale(1.05);
        }

        .post-meta {
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .post-title {
            font-family: var(--font-serif);
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
            color: var(--text-main);
            margin-bottom: 15px;
        }

        .post-excerpt {
            font-size: 1.1rem;
            color: var(--text-muted);
            margin-bottom: 20px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .read-more {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .read-more::after {
            content: '→';
            transition: transform 0.3s ease;
        }

        .post-card:hover .read-more::after {
            transform: translateX(5px);
        }

        .error {
            background-color: #fff5f5;
            color: #c53030;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #feb2b2;
            text-align: center;
        }

        .nav-actions {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
        }

        .btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #f59e0b;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0.9;
        }

        .btn-secondary {
            background-color: transparent;
            color: var(--text-main);
            border: 1px solid var(--border-color);
        }

        .btn-danger {
            background-color: #e53e3e;
            color: white;
        }

        @media (max-width: 600px) {
            h1 { font-size: 2.5rem; }
            .post-title { font-size: 1.8rem; }
            .post-img-container { height: 300px; }
            body { padding: 40px 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="subtitle">The Daily Journal</div>
            <h1>ThoughtNest – Place where ideas live</h1>
            <div class="nav-actions">
                <a href="{{ url_for('create_post') }}" class="btn">Create New Post</a>
            </div>
        </header>

        <main class="posts-grid">
            {% if posts %}
                {% for post in posts %}
                    <a href="{{ url_for('post_detail', post_id=post.id) }}" class="post-card" style="animation-delay: {{ loop.index0 * 0.1 if loop.index0 < 20 else 2 }}s">
                        <div class="post-img-container">
                            <img class="post-img" src="https://picsum.photos/900/600?random={{ post.id }}" alt="{{ post.title }}" loading="lazy">
                        </div>
                        <div class="post-meta">Story ID: {{ post.id }} • Author {{ post.userId }}</div>
                        <h2 class="post-title">{{ post.title }}</h2>
                        <p class="post-excerpt">{{ post.body }}</p>
                        <div class="read-more">Read Full Story</div>
                    </a>
                {% endfor %}
            {% else %}
                <div class="error">
                    <strong>Unable to load stories.</strong>
                </div>
            {% endif %}
        </main>
    </div>
</body>
</html>
"""

# HTML template for post detail
DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Detail | Editorial</title>
    <!-- Premium Typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #fcf9aa;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --accent-color: #0056b3;
            --border-color: #eeeeee;
            --card-bg: #ffffff;
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Inter', sans-serif;
            --max-width: 740px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.8;
            padding: 60px 20px;
        }
        
        .container {
            max-width: var(--max-width);
            margin: 0 auto;
            animation: fadeInUp 0.8s ease-out forwards;
        }
        
        .back-link {
            display: inline-flex;
            align-items: center;
            color: var(--text-muted);
            text-decoration: none;
            margin-bottom: 50px;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: color 0.3s ease;
        }
        
        .back-link:hover {
            color: var(--text-main);
        }

        .back-link::before {
            content: '←';
            margin-right: 8px;
        }
        
        .post-header {
            margin-bottom: 50px;
        }
        
        .post-meta {
            font-size: 0.9rem;
            color: var(--accent-color);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 15px;
        }
        
        .post-title {
            font-family: var(--font-serif);
            font-size: 3.2rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.1;
            margin-bottom: 25px;
            letter-spacing: -0.02em;
        }

        .post-author-box {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 15px 0;
            margin-bottom: 40px;
        }

        .author-name {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .post-image-container {
            margin: 40px 0;
        }
        
        .post-image-container img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        
        .post-body {
            font-size: 1.25rem;
            color: #333;
            margin-top: 40px;
            white-space: pre-line;
            font-family: serif;
            line-height: 1.9;
        }

        /* Comments Section Styling */
        .comments-header {
            margin-top: 80px;
            margin-bottom: 40px;
            border-top: 2px solid var(--text-main);
            padding-top: 40px;
        }

        .comments-title {
            font-family: var(--font-serif);
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .comment {
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            opacity: 0;
            animation: fadeInUp 0.6s ease forwards;
        }

        .comment:last-child {
            border-bottom: none;
        }

        .comment-header {
            margin-bottom: 10px;
        }

        .comment-author {
            font-weight: 700;
            color: var(--text-main);
            font-size: 1rem;
        }

        .comment-email {
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 500;
        }

        .comment-body {
            font-size: 1.05rem;
            color: #444;
            line-height: 1.6;
        }
        
        .error {
            background-color: #fff5f5;
            color: #c53030;
            border-radius: 4px;
            border: 1px solid #feb2b2;
            padding: 30px;
            text-align: center;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            background-color: var(--text-main);
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            gap: 8px;
        }

        .btn-small {
            padding: 4px 12px;
            font-size: 0.8rem;
        }

        .btn-secondary {
            background-color: #666;
            color: white;
        }

        .btn-danger {
            background-color: #e53e3e;
            color: white;
        }

        .comment-form {
            background: #f9f9f9;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 50px;
            border: 1px solid var(--border-color);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        .form-control {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-family: inherit;
            font-size: 1rem;
        }

        .comment-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }

        .edit-comment-form {
            display: none;
            margin-top: 15px;
        }

        @media (max-width: 600px) {
            .post-title { font-size: 2.2rem; }
            body { padding: 40px 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <nav style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 50px;">
            <a href="{{ url_for('index') }}" class="back-link" style="margin-bottom: 0;">Back to Journal</a>
            {% if post %}
                <form action="{{ url_for('delete_post', post_id=post.id) }}" method="POST" style="margin: 0;">
                    <button type="submit" class="btn btn-small btn-danger" onclick="return confirm('Are you sure you want to delete this post? This action cannot be undone.')">Delete Post</button>
                </form>
            {% endif %}
        </nav>
        
        {% if post %}
            <article>
                <header class="post-header">
                    <div class="post-meta">Story ID: {{ post.id }} • Archive</div>
                    <h1 class="post-title">{{ post.title }}</h1>
                    <div class="post-author-box">
                        By <span class="author-name">{{ user.name }}</span> • @{{ user.username }}
                    </div>
                </header>
                
                <div class="post-image-container">
                    <img src="https://picsum.photos/1200/800?random={{ post.id }}" alt="{{ post.title }}">
                </div>
                
                <div class="post-body">
                    {{ post.body }}
                </div>
            </article>

            <section>
                <div class="comments-header">
                    <h2 class="comments-title">Discussion ({{ comments|length }})</h2>
                </div>

                <!-- Add Comment Form -->
                <div class="comment-form">
                    <h3 style="margin-bottom: 20px; font-family: var(--font-serif);">Share Your Thoughts</h3>
                    <form action="{{ url_for('add_comment', post_id=post.id) }}" method="POST">
                        <div class="form-group">
                            <label for="name">Your Name</label>
                            <input type="text" name="name" id="name" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label for="email">E-mail Address</label>
                            <input type="email" name="email" id="email" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label for="body">Your Comment</label>
                            <textarea name="body" id="body" rows="4" class="form-control" required></textarea>
                        </div>
                        <button type="submit" class="btn">Post Comment</button>
                    </form>
                </div>

                <div class="comments-list">
                    {% for comment in comments %}
                        <div id="comment-{{ comment.id }}" class="comment" style="animation-delay: {{ 0.2 + (loop.index0 * 0.05) if loop.index0 < 20 else 1.5 }}s">
                            <div class="comment-header">
                                <div class="comment-author">{{ comment.name }}</div>
                                <div class="comment-email">{{ comment.email }}</div>
                            </div>
                            <div class="comment-body" id="body-{{ comment.id }}">{{ comment.body }}</div>
                            
                            <div class="comment-actions">
                                <button onclick="toggleEdit('{{ comment.id }}')" class="btn btn-small btn-secondary">Edit</button>
                                <form action="{{ url_for('delete_comment', comment_id=comment.id) }}" method="POST" style="display: inline;">
                                    <input type="hidden" name="post_id" value="{{ post.id }}">
                                    <button type="submit" class="btn btn-small btn-danger" onclick="return confirm('Are you sure you want to delete this comment?')">Delete</button>
                                </form>
                            </div>

                            <!-- Edit Form (Hidden by default) -->
                            <form id="edit-form-{{ comment.id }}" action="{{ url_for('edit_comment', comment_id=comment.id) }}" method="POST" class="edit-comment-form">
                                <input type="hidden" name="post_id" value="{{ post.id }}">
                                <div class="form-group">
                                    <textarea name="body" class="form-control" rows="3" required>{{ comment.body }}</textarea>
                                </div>
                                <div style="display: flex; gap: 10px;">
                                    <button type="submit" class="btn btn-small">Save Changes</button>
                                    <button type="button" onclick="toggleEdit('{{ comment.id }}')" class="btn btn-small btn-secondary">Cancel</button>
                                </div>
                            </form>
                        </div>
                    {% endfor %}
                </div>
            </section>
        {% else %}
            <div class="error">
                <strong>Something went wrong.</strong>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


# HTML template for creating a post
CREATE_POST_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft New Story | Editorial</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #fcf9aa;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --accent-color: #0056b3;
            --border-color: #eeeeee;
            --card-bg: green;
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Inter', sans-serif;
            --max-width: 700px;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 60px 20px;
        }

        .container {
            max-width: var(--max-width);
            margin: 0 auto;
        }

        header {
            margin-bottom: 50px;
        }

        h1 {
            font-family: var(--font-serif);
            font-size: 2.8rem;
            margin-bottom: 10px;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            color: var(--text-muted);
            text-decoration: none;
            margin-bottom: 30px;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .back-link::before { content: '←'; margin-right: 8px; }

        .post-form {
            background: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--text-main);
        }

        .form-control {
            width: 100%;
            padding: 14px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-family: inherit;
            font-size: 1.1rem;
            transition: border-color 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-color);
        }

        .btn {
            display: inline-block;
            padding: 15px 30px;
            background-color: var(--text-main);
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            border: none;
            width: 100%;
        }

        .btn:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="{{ url_for('index') }}" class="back-link">Back to Journal</a>
        <header>
            <h1>Draft New Story</h1>
            <p style="color: var(--text-muted);">Share your voice with the world.</p>
        </header>

        <form action="{{ url_for('create_post') }}" method="POST" class="post-form">
            <div class="form-group">
                <label for="title">Headline</label>
                <input type="text" name="title" id="title" class="form-control" placeholder="Enticing Title..." required>
            </div>
            <div class="form-group">
                <label for="body">The Story</label>
                <textarea name="body" id="body" rows="10" class="form-control" placeholder="Write your content here..." required></textarea>
            </div>
            <button type="submit" class="btn">Publish Story</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Fetch and display all posts"""
    try:
        # Use cached posts or fetch if not ready
        if api_cache['posts']:
            api_posts = api_cache['posts'][:20]
        else:
            response = requests.get('https://jsonplaceholder.typicode.com/posts')
            api_posts = response.json()[:20]
        
        # Filter deleted API posts
        if 'deleted_post_ids' in globals():
            api_posts = [p for p in api_posts if p['id'] not in globals()['deleted_post_ids']]
            
        # Combine API posts with local posts
        all_posts = local_posts + api_posts
        return render_template_string(POSTS_TEMPLATE, posts=all_posts)
    except Exception as e:
        return render_template_string(POSTS_TEMPLATE, posts=local_posts)

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        
        new_post = {
            'id': 101 + len(local_posts), # Offset from API IDs
            'userId': 1,
            'title': title,
            'body': body
        }
        local_posts.insert(0, new_post)
        return redirect(url_for('index'))
    return render_template_string(CREATE_POST_TEMPLATE)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Fetch and display a single post with user details and comments"""
    try:
        # Check local posts first
        post = next((p for p in local_posts if p['id'] == post_id), None)
        
        if not post:
            if api_cache['posts']:
                post = next((p for p in api_cache['posts'] if p['id'] == post_id), None)
            
            if not post:
                post_response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}')
                post = post_response.json()
        
        # Mock user info
        user_id = post.get('userId', 1)
        user = None
        try:
            if api_cache['users']:
                user = next((u for u in api_cache['users'] if u['id'] == user_id), None)
                
            if not user:
                user_response = requests.get(f'https://jsonplaceholder.typicode.com/users/{user_id}')
                user = user_response.json()
        except:
            user = {"name": "Anonymous Author", "username": "anonymous"}

        # Fetch API comments
        try:
            if api_cache['comments']:
                api_comments = [c for c in api_cache['comments'] if c['postId'] == post_id]
            else:
                comments_response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}/comments')
                api_comments = comments_response.json()
        except:
            api_comments = []

        # Filter out deleted API comments
        if 'deleted_comment_ids' in globals():
            api_comments = [c for c in api_comments if c['id'] not in globals()['deleted_comment_ids']]

        # Filter local comments for this post
        post_local_comments = [c for c in local_comments if c['postId'] == post_id]
        
        all_comments = post_local_comments + api_comments
        
        return render_template_string(DETAIL_TEMPLATE, post=post, user=user, comments=all_comments)
    except Exception as e:
        print(f"Error in post_detail: {e}")
        return render_template_string(DETAIL_TEMPLATE, post=None, user=None, comments=[])

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    global comment_id_counter
    name = request.form.get('name')
    email = request.form.get('email')
    body = request.form.get('body')
    
    new_comment = {
        'id': comment_id_counter,
        'postId': post_id,
        'name': name,
        'email': email,
        'body': body
    }
    local_comments.insert(0, new_comment)
    comment_id_counter += 1
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    post_id = request.form.get('post_id')
    new_body = request.form.get('body')
    
    # Check if it's a local comment
    comment = next((c for c in local_comments if c['id'] == comment_id), None)
    if comment:
        comment['body'] = new_body
    else:
        # If it's an API comment, we can't edit it remotely, but we can simulate it locally
        # This is optional, but for UX we can "shadow" it
        simulated_edit = {
            'id': comment_id,
            'postId': int(post_id),
            'body': new_body,
            'name': 'Edited Comment', # Placeholder for name/email
            'email': 'edited@example.com'
        }
        # For simplicity, we only edit local comments in this implementation
        # Or we could fetch and then modify locally. Let's stick to local comments for now.
        pass

    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    post_id = request.form.get('post_id')
    global local_comments
    local_comments = [c for c in local_comments if c['id'] != comment_id]
    
    # To "delete" an API comment, we'd need a list of deleted_comment_ids
    # Let's add that for completeness
    if 'deleted_comment_ids' not in globals():
        globals()['deleted_comment_ids'] = []
    
    if comment_id < 501: # API comment range
        globals()['deleted_comment_ids'].append(comment_id)

    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    global local_posts
    # Remove from local if it exists
    local_posts = [p for p in local_posts if p.get('id') != post_id]
    
    # If it's an API post, mark as deleted
    if 'deleted_post_ids' not in globals():
        globals()['deleted_post_ids'] = []
    
    if post_id <= 100:
        globals()['deleted_post_ids'].append(post_id)
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

