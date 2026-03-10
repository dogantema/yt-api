from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

def get_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
    }

@app.route('/')
def home():
    return jsonify({
        'status': 'API calisiyor',
        'endpoints': {
            'GET /info?url=': 'Video bilgisi + tum formatlar',
            'GET /formats?url=': 'Sadece video+ses formatlar',
            'GET /download?url=&format_id=': 'Direkt indirme linki',
            'GET /mp3?url=': 'En iyi ses linki',
        }
    })

@app.route('/info')
def info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url parametresi gerekli'}), 400
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            data = ydl.extract_info(url, download=False)
        formats = []
        for f in data.get('formats', []):
            formats.append({
                'format_id':  f.get('format_id'),
                'ext':        f.get('ext'),
                'resolution': f.get('resolution') or 'audio only',
                'fps':        f.get('fps'),
                'filesize':   f.get('filesize'),
                'url':        f.get('url'),
            })
        return jsonify({
            'title':      data.get('title'),
            'channel':    data.get('uploader'),
            'duration':   data.get('duration'),
            'thumbnail':  data.get('thumbnail'),
            'formats':    formats,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/formats')
def formats():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url parametresi gerekli'}), 400
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            data = ydl.extract_info(url, download=False)
        result = []
        for f in data.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                result.append({
                    'format_id':  f.get('format_id'),
                    'ext':        f.get('ext'),
                    'resolution': f.get('resolution'),
                    'fps':        f.get('fps'),
                    'filesize':   f.get('filesize'),
                    'url':        f.get('url'),
                })
        return jsonify({'title': data.get('title'), 'formats': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    format_id = request.args.get('format_id', 'best')
    if not url:
        return jsonify({'error': 'url parametresi gerekli'}), 400
    try:
        opts = get_ydl_opts()
        opts['format'] = format_id
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        chosen = data.get('requested_formats') or [data]
        f = chosen[0]
        return jsonify({
            'title':      data.get('title'),
            'ext':        f.get('ext'),
            'resolution': f.get('resolution'),
            'url':        f.get('url'),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mp3')
def mp3():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url parametresi gerekli'}), 400
    try:
        opts = get_ydl_opts()
        opts['format'] = 'bestaudio'
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        return jsonify({
            'title':    data.get('title'),
            'ext':      data.get('ext'),
            'filesize': data.get('filesize'),
            'url':      data.get('url'),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
