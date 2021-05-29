import {FileResponseData} from "./FilesAPI";
import axios from "axios";
import {ImageResponseData} from "./ImagesAPI";
import {VideoShowResponseData} from "./VideoShowsAPI";
import {MultipleResponseData, ResponseData} from "./API";
import {DownloadResponseData} from "./DownloadsAPI";

export interface VideosBrowseResponseData extends ResponseData {
    videos: Array<VideoResponseData>,
    downloads: Array<DownloadResponseData>
}

export interface VideoResponseData extends ResponseData {
    api_detail_url: string
    // associations TODO
    deck: string
    guid: string
    hd_url: string
    high_url: string
    low_url: string
    embed_player: string
    id: number
    image_id: number
    image?: ImageResponseData
    length_seconds: number
    name: string
    publish_date: string
    site_detail_url: string
    url: string
    user: string
    // video_categories TODO
    video_show_id: number
    video_show?: VideoShowResponseData
    youtube_id: string
    saved_time: string
    premium: boolean
    hosts: string
    crew: string
}

export interface VideosGetFilters {
    id?: number | number[]
}

export interface VideosBrowseFilters {
    page?: number
    id?: number | number[]
    video_show?: number | number[]
    sort_field?: string
    sort_direction?: string
}

export default class VideosAPI {
    public static get(args: VideosGetFilters) {
        return axios.post<MultipleResponseData<VideoResponseData>>(`/api/videos/get`, args);
    }

    public static getOne(args: VideosGetFilters) {
        return axios.post<VideoResponseData>(`/api/videos/get-one`, args);
    }

    public static browse(args: VideosBrowseFilters) {
        return axios.post<VideosBrowseResponseData>(`/api/videos/browse`, args);
    }
}