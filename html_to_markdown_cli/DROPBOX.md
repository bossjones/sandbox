# aiodbx

Rough async Python implementation of the Dropbox HTTP API using aiohttp. Primarily created to speed up large batch upload/download tasks, which are heavily bottlenecked by the official Python library's synchronous requests.

Check out `example.py` for a simple use case which downloads some files, modifies them and re-uploads them.

## Implementation

Below is a list of implemented endpoints and their corresponding methods in the `AsyncDropboxAPI` class.

| Endpoint                                                     | Method name              |
| ------------------------------------------------------------ | ------------------------ |
| [/check/user](https://www.dropbox.com/developers/documentation/http/documentation#check-user) | validate                 |
| [/download](https://www.dropbox.com/developers/documentation/http/documentation#files-download) | download_file            |
| [/download_zip](https://www.dropbox.com/developers/documentation/http/documentation#files-download_zip) | download_folder          |
| [/get_shared_link_file](https://www.dropbox.com/developers/documentation/http/documentation#sharing-get_shared_link_file) | download_shared_link     |
| [/upload](https://www.dropbox.com/developers/documentation/http/documentation#files-upload) | upload_single            |
| [/upload_session/start](https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-start) | upload_start             |
| [/upload_session/finish_batch](https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-finish_batch), [/upload_session/finish_batch/check](https://www.dropbox.com/developers/documentation/http/documentation#files-upload_session-finish_batch) | upload_finish*           |
| [/create_shared_link_with_settings](https://www.dropbox.com/developers/documentation/http/documentation#sharing-create_shared_link_with_settings) | create_shared_link       |
| [/get_shared_link_metadata](https://www.dropbox.com/developers/documentation/http/documentation#sharing-get_shared_link_metadata) | get_shared_link_metadata |

\* Batch job completion is checked automatically.
