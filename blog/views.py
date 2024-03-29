from django.db.models import Count, Prefetch
from django.shortcuts import render
from blog.models import Comment, Post, Tag
from blog.serialize_tools import serialize_tag, serialize_post


def index(request):
    most_popular_posts = Post.objects.popular() \
                             .prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(posts_number=Count('posts'))))[:5] \
        .fetch_with_comments_count()

    fresh_posts = Post.objects.prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(posts_number=Count('posts')))
    ) \
        .annotate(comments_count=Count('comments')).order_by('published_at')

    most_fresh_posts = list(fresh_posts)[-5:]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.prefetch_related('author').get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': post.author,
        })

    likes = post.likes.all()

    related_tags = post.tags.annotate(posts_number=Count('posts'))

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular() \
                             .prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(posts_number=Count('posts'))))[:5] \
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
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular() \
                             .prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(posts_number=Count('posts'))))[:5] \
        .fetch_with_comments_count()

    related_posts = Post.objects.filter(tags__title=tag_title).prefetch_related(
        'author',
        Prefetch('tags', queryset=Tag.objects.annotate(posts_number=Count('posts')))
    )[:20].fetch_with_comments_count()

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
