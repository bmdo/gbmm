import {ImageResponseData} from "./ImagesAPI";
import {VideoResponseData} from "./VideosAPI";
import {MultipleResponseData, ResponseData} from "./API";
import axios from "axios";

export interface VideoShowResponseData extends ResponseData {
    /** URL pointing to the detail resource. */
    api_detail_url: string
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
    image_id: number
    /** Main image of the video_show. */
    image?: ImageResponseData
    /** ID of the show logo. */
    logo_id: number
    /** Show logo. */
    logo?: ImageResponseData
    /** Is this show currently active */
    active: boolean
    /** Should this show be displayed in navigation menus */
    display_nav: string
    /** The latest episode of a video show. Overrides other sorts when used as a sort field. */
    // latest
    /** Premium status of video_show. */
    premium: boolean
    /** Endpoint to retrieve the videos attached to this video_show. */
    api_videos_url: string
    /** URL pointing to the show on Giant Bomb. */
    site_detail_url: string
    /** Videos associated with this show. */
    videos?: VideoResponseData[]
}

export default class VideoShowsAPI {
    public static getAll() {
        return axios.get<MultipleResponseData<VideoShowResponseData>>(`/api/video-shows/get-all`);
    }
}