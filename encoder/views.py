from datetime import datetime

from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from encoder import models as encoder
from encoder import forms as forms
from encoder.templatetags.encoder import link_seek


def get_username(request):
    if request.user.is_authenticated():
        return request.user.username
    else:
        return None

def add_notification(request, comment_id):
    if not request.POST:
        raise Http404
    comment = get_object_or_404(encoder.Comment,
                                id=comment_id,
                                commenter=request.user)
    comment_notification_form = forms.CommentNotificationForm(data=request.POST,
                                                              request=request,
                                                              comment=comment)
    if comment_notification_form.is_valid():
        comment_notification_form.instance.sender = request.user
        comment_notification_form.instance.created_time = datetime.now()
        comment_notification_form.instance.comment = comment
        comment_notification_form.save()
    return redirect(comment.media.get_absolute_url())

def delete_notification(request, notification_id):
    notification = get_object_or_404(encoder.CommentNotification,
                                     id=notification_id,
                                     receiver=request.user)
    notification.delete()
    return redirect(notification.comment.media.get_absolute_url())

def media_player(request, identifier):
    media = encoder.Media.objects.get(identifier=identifier)
    comments = media.commments.order_by('created_time')
    comment_form = forms.CommentForm()

    if request.POST:
        comment_form = forms.CommentForm(request.POST, request=request)
        if comment_form.is_valid():
            comment_form.instance.commenter = request.user
            comment_form.instance.media = media
            comment_form.save()

    for c in comments:
        c.comment_notification_form = forms.CommentNotificationForm(request,
                                                                    comment=c)
    
    seek_time = request.GET.get('time', None)
    if seek_time:
        min, sec = seek_time.split(':')
        seek_time = int(min)*60 + int(sec)
    context = RequestContext(request, {
        'username': get_username(request),
        'media': media,
        'comments': comments,
        'description': link_seek(media.description),
        'comment_form': comment_form,
        'seek_time': seek_time})
    try:
        v = media.video
        return render_to_response('encoder/demo/video_player.html', context)
    except ObjectDoesNotExist:
        return render_to_response('encoder/demo/audio_player.html', context)


def delete_comment(request, comment_id):
    comment = get_object_or_404(encoder.Comment, id=comment_id)
    if comment.commenter != request.user:
        return HttpResponseForbidden()
    context = RequestContext(request, {
        'username': request.user.username,
        'comment': comment})
    return render_to_response('encoder/delete_comment.html', context)


def delete_comment_confirm(request, comment_id):
    comment = get_object_or_404(encoder.Comment, id=comment_id)
    if request.POST:
        if comment.commenter != request.user:
            return HttpResponseForbidden()
        comment.delete()
    return redirect(reverse('home'))


def media_query(t):
    return Q(title__icontains=t) | Q(description__icontains=t) | Q(original_filename__icontains=t)

def comments_query(t):
    return Q(text__icontains=t)

def collections_query(t):
    return Q(slug__icontains=t)

def search(query, query_func, qs):
    q = Q()
    for t in query.split(' '):
        q |= query_func(t)
    return qs.filter(q)

def home(request):
    collections = encoder.Collection.objects.order_by('slug')
    comments = encoder.Comment.objects.order_by('-created_time')[:10]
    media = encoder.Media.objects.none
    search_query = request.GET.get('q', None)
    sent, received = None, None
    if not request.user.is_anonymous():
        sent = request.user.sent_notifications.filter(seen_time__isnull=True).order_by('created_time')
        received = request.user.received_notifications.filter(seen_time__isnull=True).order_by('created_time')
    context = {
        'username': get_username(request),
        'comments': comments,
        'collections': collections,
        'media': media,
        'search_query': search_query, 
        'sent': sent,
        'received': received,
    }
    if search_query:
        context.update({
            'collections': search(search_query, collections_query,
                                 encoder.Collection.objects.all().order_by('slug')),
            'comments': search(search_query, comments_query,
                               encoder.Comment.objects.all().order_by('-created_time')),
            'media': search(search_query, media_query,
                            encoder.Media.objects.encoded().order_by('-encode_start_time')),
        })
    return render_to_response('encoder/home.html', context)


def collection(request, collection_slug):
    collection = encoder.Collection.objects.get(slug=collection_slug)
    comments = encoder.Comment.objects.filter(media__collection=collection).order_by('-created_time')[:15]
    search_query = request.GET.get('q', None)
    if search_query:
        media = search(search_query, media_query, encoder.Media.objects.filter(collection=collection))
    else:
        media = collection.media.encoded().order_by('-encode_end_time')
    paginator = Paginator(media, 10)
    page = request.GET.get('page', 1)
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    context = {
        'comments': comments,
        'page': page,
        'collection': collection,
        'search_query': search_query,
    }
    return render_to_response('encoder/collection.html', context)


@login_required
def encode_collection(request, collection_slug):
    encoder.Collection.objects.get(slug=collection_slug).encode()
    return redirect('/admin/encoder/collection')


@login_required
def import_collection(request, collection_slug):
    c = encoder.Collection.objects.get(slug=collection_slug)
    c.import_media()
    return redirect('/admin/encoder/collection/' + str(c.id))
