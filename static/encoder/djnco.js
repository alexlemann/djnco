function show_video_player(identifier) {
  var pre = 'http://libstream.dhcp.bsu.edu/';
  var url_low = pre + identifier + '-600.mp4'
  var url_high = pre + identifier + '-1024.mp4'
  flowplayer('player', '/static/encoder/flowplayer/flowplayer-3.2.7.swf', {
    clip: { 
      scaling: 'fit',
      urlResolvers: 'bwcheck',
      autoPlay: false,
      provider: 'pseudo',
      bitrates: [
        { url: url_low, bitrate: 300, isDefault: true, normal: true },
        { url: url_high, bitrate: 1024, isDefault: false, hd: true }
      ],
    },
    plugins: { 
      controls: { autoHide: false },
      pseudo: { url: '/static/encoder/flowplayer/flowplayer.pseudostreaming-3.2.7.swf' },
      viral: { url: '/static/encoder/flowplayer/flowplayer.viralvideos-3.2.5.swf' },
      bwcheck: {
        url: '/static/encoder/flowplayer/flowplayer.bwcheck-3.2.5.swf',
        serverType: 'http',
        hdButton: 'both',
        dynamic:false 
      }
    }
  });
}

function show_audio_player(identifier) {
  var pre = 'http://libstream.dhcp.bsu.edu/';
  var url = pre + identifier + '.mp3'
  flowplayer('audio_player', '/static/encoder/flowplayer/flowplayer-3.2.7.swf', {
    clip: { 
      autoPlay: false,
      url : url,
    },
    plugins: { 
      audio: { url: '/static/encoder/flowplayer/flowplayer.audio-3.2.2.swf' },
      controls: { 
          fullscreen: false,
          height: 25,
          autoHide: false
      }
    }
  });
}

function load_player(identifier, show_player_f) {
    var uagent = navigator.userAgent.toLowerCase();
    var result = uagent.search("ipod|iphone");
    if (result != -1) {
      $('#ios_' + identifier).show();
    }
    else {
      $('#nonios_' + identifier).show();
      show_player_f(identifier);
    }
}

function load_audio_player(identifier) {
    load_player(identifier, show_audio_player);
}

function load_video_player(identifier) {
    load_player(identifier, show_video_player);
}

function seek(time) {
    if ($f('player').isPlaying()) {
      $f('player').seek(time);
    } else { 
      $f('player').play(); 
      setTimeout(function() {
        $f('player').seek(time);
      }, (2000));
    }
}
