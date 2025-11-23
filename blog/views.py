from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.db.models import Prefetch

def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def serialize_post(post):

    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def index(request):

    tags_with_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_count)

    most_popular_posts = Post.objects.popular()[:5] \
                       .prefetch_related('author', prefetch_tags) \
                       .fetch_with_comments_count()

    most_fresh_posts = Post.objects.order_by()[:5] \
                        .prefetch_related('author', prefetch_tags) \
                        .fetch_with_comments_count()

    most_popular_tags = Tag.objects.annotate(
        posts_count=Count('posts')
    ).popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post(post) for post in most_fresh_posts
        ],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tags_with_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_count)

    post = Post.objects.prefetch_related('author', prefetch_tags)\
               .annotate(
                   comments_count=Count('comments'),
                   likes_count=Count('likes')
               ).get(slug=slug)

    post.comments_count = post.comments.count()

    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.annotate(
        posts_count=Count('posts')
    ).popular()[:5]

    most_popular_posts = Post.objects.popular()\
                       .prefetch_related('author', prefetch_tags)[:5]\
                       .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tags_with_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_count)

    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.annotate(
        posts_count=Count('posts')
    ).popular()[:5]

    most_popular_posts = Post.objects.popular()\
                       .prefetch_related('author', prefetch_tags)[:5]\
                       .fetch_with_comments_count()

    related_posts = tag.posts.prefetch_related('author', prefetch_tags)[:20]
    related_posts_ids = [post.id for post in related_posts]
    comments_data = Post.objects.filter(id__in=related_posts_ids) \
        .annotate(comments_count=Count('comments')) \
        .values_list('id', 'comments_count')
    comments_map = dict(comments_data)

    for post in related_posts:
        post.comments_count = comments_map.get(post.id, 0)

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
