<h1 style="text-align: center">gbmm</h1>
<p style="text-align: center">A Giant Bomb media manager.</p>

## Setup

### Docker
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

### Manual setup
It's also possible to set up gbmm without Docker.

### General setup notes

#### API Key
A Giant Bomb API key is required to set up gbmm. gbmm will prompt you for an API key on first startup.

To get an API key, you must sign up for an account on Giant Bomb. If you already have a Giant Bomb API account, head to https://www.giantbomb.com/api/ to find your API key.

#### Media file storage location
The structure and name of media files is predetermined and is tracked by the gbmm database.
Files are saved under a subdirectory tree created under the chosen media file storage location. 

Notes on selecting a media file storage location:
* It's best to create an empty directory for this location. It is possible gbmm will overwrite existing data in this directory if there are any preexisting files.
* Choose a location plenty of storage space. Individual video files are frequently multiple gigabytes in size, and your storage usage can increase quickly when downloading many videos.

## Overview

gbmm allows for browsing and downloading videos and their associated images from <a href="https://www.giantbomb.com/">Giant Bomb</a>.

### Features
* Video browser with filters and sorting
* Ability to download videos from the video browser
* Download queue
* Metadata stored locally for entirely offline access to downloaded content