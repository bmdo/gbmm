import Loadable from "./Loadable";
import {ImageResponseData} from "./gbmmapi/ImagesAPI";
import API, {validResponseData} from "./gbmmapi/API";
import {VideoShowResponseData} from "./gbmmapi/VideoShowsAPI";
import ResultList from "./ResultList";

export default class VideoShow extends Loadable {
    /** URL pointing to the detail resource. */
    apiDetailUrl: string
    /** Brief summary of the video_show. */
    deck: string
    /** Cross-entity unique ID */
    guid: string
    /** Title of the video_show. */
    title: string
    /** Editor ordering. */
    position: string
    /** Unique ID of the show. */
    id: number
    /** ID of the main image of the video_show. */
    imageId: number
    /** Main image of the video_show. */
    image?: ImageResponseData
    /** ID of the show logo. */
    logoId: number
    /** Show logo. */
    logo?: ImageResponseData
    /** Is this show currently active */
    active: boolean
    /** Should this show be displayed in navigation menus */
    displayNav: string
    /** The latest episode of a video show. Overrides other sorts when used as a sort field. */
    // latest
    /** Premium status of video_show. */
    premium: boolean
    /** Endpoint to retrieve the videos attached to this video_show. */
    apiVideosUrl: string
    /** URL pointing to the show on Giant Bomb. */
    siteDetailUrl: string
    /** Videos associated with this show. */
    // videos?: Video[]

    public constructor(data?: VideoShowResponseData) {
        super();
        if (!validResponseData(data)) {
            this.loadFailed = true;
            return;
        }
        this.apiDetailUrl = data.api_detail_url;
        this.deck = data.deck;
        this.guid = data.guid;
        this.title = data.title;
        this.position = data.position;
        this.id = data.id;
        this.imageId = data.image_id;
        this.image = data.image ?? null;
        this.logoId = data.logo_id;
        this.logo = data.logo ?? null;
        this.active = data.active;
        this.displayNav = data.display_nav;
        this.premium = data.premium;
        this.apiVideosUrl = data.api_videos_url;
        this.siteDetailUrl = data.site_detail_url;
    }

    public static async getAll() {
        let response = await API.videoShows.getAll();
        return new ResultList(VideoShow, response.data);
    }
}