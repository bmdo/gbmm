import Loadable from "./Loadable";
import Definitions from "./Definitions";
import {ImageResponseData} from "./gbdlapi/ImagesAPI";
import API, {validResponseData} from "./gbdlapi/API";
import VideoShowsAPI, {VideoShowResponseData} from "./gbdlapi/VideoShowsAPI";
import Video from "./Video";
import ResultList from "./ResultList";
import {VideoCategoryResponseData} from "./gbdlapi/VideoCategoriesAPI";

export default class VideoCategory extends Loadable {
    /** URL pointing to the video_category detail resource. */
    apiDetailUrl: string
    /** Brief summary of the video_category. */
    deck: string
    /** Unique ID of the video_category. */
    id: number
    /** Name of the video_category. */
    name: string
    imageId: number
    /** Main image of the video_category. */
    image: ImageResponseData
    /** URL pointing to the video_category on Giant Bomb. */
    siteDetailUrl: string

    public constructor(data?: VideoCategoryResponseData) {
        super();
        if (!validResponseData(data)) {
            this.loadFailed = true;
            return;
        }
        this.apiDetailUrl = data.api_detail_url;
        this.deck = data.deck;
        this.id = data.id;
        this.name = data.name;
        this.imageId = data.image_id;
        this.image = data.image ?? null;
        this.siteDetailUrl = data.site_detail_url;
    }

    public static async getAll() {
        let response = await API.videoCategories.getAll();
        return new ResultList(VideoCategory, response.data);
    }
}