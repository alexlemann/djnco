from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse

from encoder import models as encoder 
from encoder import forms as forms
from encoder.templatetags.encoder import link_seek

def get_username(request):
    if request.user.is_authenticated():
        return request.user.username
    else:
        return None

def demo_video(request, identifier):
    v = encoder.Video.objects.get(identifier=identifier)
    comments = v.media_ptr.commments.order_by('created_time')
    comment_form = forms.CommentForm()
    if request.POST:
      comment_form = forms.CommentForm(request.POST, request=request)
      if comment_form.is_valid():
        comment_form.instance.commenter = request.user
        comment_form.instance.media = v.media_ptr
        comment_form.save()

    context = RequestContext(request, {
      'username' : get_username(request),
      'video' : v,
      'comments' : comments,
      'description' : link_seek(v.description),
      'comment_form': comment_form
    })
    return render_to_response('encoder/demo/video.html', context)

def demo_audio(request, identifier):
    a = encoder.Audio.objects.get(identifier=identifier)
    comments = a.media_ptr.commments.all()
    if a.description:
        add_seek_links(a)
    return render_to_response('encoder/demo/audio.html', {'audio' : a,
                                                          'comments': comments})
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
    print 'post?'
    if request.POST:
        print 'post!'
        if comment.commenter != request.user:
            print 'access denied'
            return HttpResponseForbidden()
        print 'delete'
        comment.delete()
    return redirect(reverse('home'))

def home(request):
    videos = encoder.Video.objects.order_by('-encode_end_time')
    sounds = encoder.Audio.objects.order_by('-encode_end_time')
    comments = encoder.Comment.objects.order_by('-created_time')[:10]
    context = {
        'videos' : videos,
        'sounds' : sounds,
        'username': get_username(request),
        'comments' : comments
    }
    return render_to_response('encoder/home.html', context)

@login_required
def encode_collection(request, collection_slug):
    encoder.Collection.objects.get(slug=collection_slug).encode()
    return redirect('/admin/encoder/collection')

@login_required
def import_collection(request, collection_slug):
    c = encoder.Collection.objects.get(slug=collection_slug)
    c.import_media()
    return redirect('/admin/encoder/collection/' + str(c.id) )
