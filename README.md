# convert-to-mp3s

Batch-archives a YouTube channel's back-catalog as MP3s, organized by playlist.

Built to turn a few hundred recorded talks into an audio archive that could be listened to offline. Written to survive a long unattended run on a small cloud instance: it downloads, transcodes, and deletes the source video before moving on, so disk usage stays flat regardless of how many videos are in the batch, and it resumes where it left off rather than starting over.

## How it works

Two stages, run in order:

**1. Build the manifest.** `save_config_from_YT_api.py` walks every playlist on a channel through the YouTube Data API and writes `config.json` — a map of playlist → video → `{title, upload_date, link}`. Paging is handled, so playlists longer than the API's 50-item response are followed to the end.

**2. Download and transcode.** `convert.py` reads the manifest, and for each video in the selected playlists downloads the progressive MP4, transcodes it to MP3 with `ffmpeg`, then removes the MP4. Output is named `{title}_{date}.mp3` and filed under a per-playlist folder.

`rename.py` is a one-off repair pass: it re-derives correct dates from the manifest and renames files from an earlier run that were saved with the wrong timestamps.

### Design notes

- **Resumable.** Before downloading, it checks whether the destination MP3 already exists and skips it. A run that dies halfway can simply be restarted.
- **Flat disk usage.** The MP4 is deleted immediately after transcoding, so peak disk is one video, not the whole batch.
- **Failures don't stop the batch.** Per-video exceptions are logged and collected into a failure set; the run continues. Progress goes to `logfile.log` with timestamps and an `n of N` counter.

## Setup

Requires `ffmpeg` on the PATH and a YouTube Data API key:

```bash
pip install -r requirements.txt
export YOUTUBE_API_KEY="your-key-here"
```

Then set the paths marked `# TODO: set local path` at the top of each script, and put the target channel ID and the playlists you want in `save_config_from_YT_api.py` and `convert.py` respectively.

```bash
python code/save_config_from_YT_api.py   # writes config.json
python code/convert.py                   # downloads and transcodes
```

## Caveats

- `pytube` breaks whenever YouTube changes its player; if downloads start failing with regex or cipher errors, that's the cause, and the fix is upgrading or patching pytube rather than anything in this repo.
- Downloading is subject to YouTube's Terms of Service. This was written for archiving a channel's own content.
