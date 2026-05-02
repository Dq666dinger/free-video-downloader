from app.services.ytdlp import build_format_candidates


def test_build_format_candidates_marks_direct_and_mux_options():
    info = {
        "formats": [
            {
                "format_id": "22",
                "url": "https://cdn.example.com/video-720.mp4",
                "ext": "mp4",
                "vcodec": "avc1.64001F",
                "acodec": "mp4a.40.2",
                "height": 720,
                "protocol": "https",
                "fps": 30,
            },
            {
                "format_id": "137",
                "url": "https://cdn.example.com/video-only-1080.mp4",
                "ext": "mp4",
                "vcodec": "avc1.640028",
                "acodec": "none",
                "height": 1080,
                "protocol": "https",
                "fps": 60,
            },
        ]
    }

    formats = build_format_candidates(info)

    assert len(formats) == 2
    assert formats[0].height == 1080
    assert formats[0].requires_ffmpeg is True
    assert formats[0].direct_available is False
    assert formats[1].direct_available is True
    assert formats[1].note == "支持极速下载和稳定下载"

