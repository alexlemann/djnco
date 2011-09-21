function show_player(identifier) {
  var pre = 'http://libmarktest.dhcp.bsu.edu/uploads/published/';
  var url_low = pre + identifier + '-600.mp4'
  var url_high = pre + identifier + '-1024.mp4'
  flowplayer('player_' + identifier, 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer-3.2.7.swf', {
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
      pseudo: { url: 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer.pseudostreaming-3.2.7.swf' },
      viral: { url: 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer.viralvideos-3.2.5.swf' },
      bwcheck: {
        url: 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer.bwcheck-3.2.5.swf',
        serverType: 'http',
        hdButton: 'both',
        dynamic:false 
      }
    }
  });
}

function detectDevice(identifier) {
    var uagent = navigator.userAgent.toLowerCase();
    var result = uagent.search("ipod|iphone");
    if (result != -1) {
      $('#ios_' + identifier).show();
    }
    else {
      $('#nonios_' + identifier).show();
      show_player(identifier);
    }
}

function playAudio(identifier) {
  var pre = 'http://libmarktest.dhcp.bsu.edu/uploads/published/';
  var url = pre + identifier + '.mp3'
  flowplayer('player_' + identifier, 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer-3.2.7.swf', {
    clip: { 
      autoPlay: false,
      url : url,
    },
    plugins: { 
      audio: { url: 'http://libmarktest.dhcp.bsu.edu/uploads/flowplayer/flowplayer.audio-3.2.2.swf' },
      controls: { fullscreen: false, height: 25, autoHide: false}
    }
  });
}
