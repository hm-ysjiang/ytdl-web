# ytdl-web
## To install python dependencies
Run
`pip install -r pip-requirements`

Using `virtualenv` is also fine.

## Embedding thumbnails
Youtube seems to have a problem that is mis-labeling its WEBP thumbnail as JPEG, which caused FFMpeg to crash while embedding thumbnails (see [youtube-dl#25687](https://github.com/ytdl-org/youtube-dl/issues/25687))

There is a PR fixing this problem ([youtube-dl#25717](https://github.com/ytdl-org/youtube-dl/pull/25717)), but it is not merged yet.

So if you want to enable thumbnail embedding, make sure you patched the fix.