<h1 style="text-align: center">gbmm</h1>
<p style="text-align: center">A Giant Bomb media manager</p>

gbmm allows for browsing and downloading videos and their associated images from <a href="https://www.giantbomb.com/">Giant Bomb</a>.

### Features
* Video browser with filters and sorting
* Ability to download videos from the video browser
* Download queue
* Metadata stored locally for entirely offline access to downloaded content

## Setup

### Using Docker
Set up of the gbmm Docker image is easiest. Head to the <a href="https://hub.docker.com/r/bmdo/gbmm">Docker Hub page</a> and pull the image to get set up quickly.

#### Parameters
<table>
    <tr>
        <td>
            <code>-p 8877</code>
        </td>
        <td>
            Web UI
        </td>
    </tr>
    <tr>
        <td>
            <code>-v /app</code>
        </td>
        <td>
            Root for application data storage, including database, log, and configuration file.
        </td>
    </tr>
    <tr>
        <td>
            <code>-v /data</code>
        </td>
        <td>
            Media file storage location (videos, images, etc.)
        </td>
    </tr>
</table>

### Using a manual setup
It's also possible to set up gbmm without Docker.

#### 1. Install python
Download the latest version of Python 3 here: https://www.python.org/downloads/

#### 2. Configure environment variables

The following environment variables allow you to configure the storage location for gbmm data.

<table>
    <tr>
        <td>
            <code>GBMM_ROOT</code>
        </td>
        <td>
            Root for application data storage, including database, log, and configuration file. Defaults to <code>/app</code>. If this directory does not exist, gbmm will fail to start.
        </td>
    </tr>
    <tr>
        <td>
            <code>GBMM_FILES</code>
        </td>
        <td>
            <span>Media file storage location for storing videos, images, etc. Defaults to <code>./files</code> (relative to <code>GBMM_ROOT</code>).</span>
            <span><strong>This is only used if you do not provide a config file with a valid file root.</strong> This is useful for configuring a desired file location on initial startup.</span>
        </td>
    </tr>
</table>

#### 3. Run the application

<code>
export FLASK_APP=server.app; python3 -m flask run --host=0.0.0.0
</code>

### General setup notes
#### Web UI
Visit port 8877 (or the port you configured for your Docker container) to access the web UI. E.g., http://127.0.0.1:8877.

#### Web server
The docker image and setup instructions above currently use werkzeug, which is a server intended for development use. While probably OK for limited use, werkzeug is not a scalable web server.

This is probably OK for a personal use application like gbmm, but you may want to <a href="https://flask.palletsprojects.com/en/2.0.x/deploying/">explore other options</a> if you want a more robust web server.


#### API Key
A Giant Bomb API key is required to set up gbmm. gbmm will prompt you for an API key on first startup.

To get an API key, you must sign up for an account on Giant Bomb. If you already have a Giant Bomb API account, head to https://www.giantbomb.com/api/ to find your API key.

#### Media file storage location
The structure and name of media files is predetermined and is tracked by the gbmm database.
Files are saved under a subdirectory tree created under the chosen media file storage location. 

Notes on selecting a media file storage location:
* It's best to create an empty directory for this location. It is possible gbmm will overwrite existing data in this directory if there are any preexisting files.
* Choose a location plenty of storage space. Individual video files are frequently multiple gigabytes in size, and your storage usage can increase quickly when downloading many videos.