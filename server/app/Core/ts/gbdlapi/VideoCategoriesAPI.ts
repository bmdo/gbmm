import {ImageResponseData} from "./ImagesAPI";
import {MultipleResponseData, ResponseData} from "./API";
import axios from "axios";

export interface VideoCategoryResponseData extends ResponseData {
    /** URL pointing to the video_category detail resource. */
    api_detail_url: string
    /** Brief summary of the video_category. */
    deck: string
    /** Unique ID of the video_category. */
    id: number
    /** Name of the video_category. */
    name: string
    image_id: number
    /** Main image of the video_category. */
    image: ImageResponseData
    /** URL pointing to the video_category on Giant Bomb. */
    site_detail_url: string
}

export default class VideoCategoriesAPI {
    public static getAll() {
        return axios.get<MultipleResponseData<VideoCategoryResponseData>>(`/api/video-categories/get-all`);
    }
}