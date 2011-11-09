from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from encoder import models as encoder
from encoder import forms as forms
from encoder.templatetags.encoder import link_seek


def get_username(request):
    if request.user.is_authenticated():
        return request.user.username
    else:
        return None


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
        'seek_time': seek_time
    })
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
        'comment': comment
    })
    return render_to_response('encoder/delete_comment.html', context)


def delete_comment_confirm(request, comment_id):
    comment = get_object_or_404(encoder.Comment, id=comment_id)
    if request.POST:
        if comment.commenter != request.user:
            return HttpResponseForbidden()
        comment.delete()
    return redirect(reverse('home'))


def home(request):
    collections = encoder.Collection.objects.order_by('slug')
    comments = encoder.Comment.objects.order_by('-created_time')[:10]
    context = {
        'username': get_username(request),
        'comments': comments,
        'collections': collections,
    }
    return render_to_response('encoder/home.html', context)


def collection(request, collection_slug):
    collection = encoder.Collection.objects.get(slug=collection_slug)
    comments = encoder.Comment.objects.filter(media__collection=collection
                                             ).order_by('-created_time')[:10]
    media = collection.media.filter(collection=collection,
                                    encoding_finished=True
                                   ).order_by('-encode_end_time')
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
