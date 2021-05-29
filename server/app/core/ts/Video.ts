import API, {validResponseData} from "./gbmmapi/API";
import {VideoResponseData, VideosBrowseFilters, VideosGetFilters} from "./gbmmapi/VideosAPI";
import {DownloadResponseData, DownloadsGetFilters} from "./gbmmapi/DownloadsAPI";
import Loadable from "./Loadable";
import Download from "./Download";
import Definitions from "./Definitions";

export default class Video extends Loadable {
    public id: number
    public name: string
    public deck: string
    public image: object
    public download: Download

    public constructor(data?: VideoResponseData) {
        super();
        if (!validResponseData(data)) {
            this.loadFailed = true;
            return;
        }

        this.id = data.id;
        this.name = data.name;
        this.deck = data.deck;
        this.image = data.image;

        this.loaded = true;
    }

    public static get(filters: DownloadsGetFilters) {
        return API.videos.getOne(filters)
            .then((response) => {
                return new Video(response.data);
            });
    }

    public static getMany(filters: VideosGetFilters) {
        return API.videos.get(filters)
            .then((response) => {
                let result = [];
                for (let videoData of response.data.results) {
                    result.push(new Video(videoData));
                }
                return result;
            });
    }

    public static async getBrowse(filters: VideosBrowseFilters) {
        let definitions = await Definitions.get();
        return API.videos.browse(filters)
            .then((response) => {
                let result = [];
                for (let videoData of response.data.videos) {
                    let video = new Video(videoData)
                    let downloadData = response.data.downloads.filter(d => d.obj_id === video.id);
                    if (downloadData.length > 0) {
                        video.download = new Download(downloadData[0], definitions)
                    }
                    result.push(video);
                }
                return result;
            });
    }
}