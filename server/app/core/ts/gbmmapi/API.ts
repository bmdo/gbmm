import DownloadsAPI from "./DownloadsAPI";
import DefinitionsAPI from "./DefinitionsAPI";
import FilesAPI from "./FilesAPI";
import VideosAPI from "./VideosAPI";
import { AxiosResponse } from "axios";
import VideoShowsAPI from "./VideoShowsAPI";
import SettingsAPI from "./SettingsAPI";
import VideoCategoriesAPI from "./VideoCategoriesAPI";
import SystemAPI from "./SystemAPI";

export interface ResponseData {

}

export interface MultipleResponseMetadata {
    limit: number
    offset: number
    current_page: number
    total_pages: number
    total_results: number
}

export interface MultipleResponseData<T> extends ResponseData {
    results: T[]
    metadata: MultipleResponseMetadata
}

export type ResponsePromise<T extends ResponseData = ResponseData> = Promise<AxiosResponse<T>>

export default class API {
    public static readonly definitions = DefinitionsAPI
    public static readonly downloads = DownloadsAPI
    public static readonly files = FilesAPI
    public static readonly videos = VideosAPI
    public static readonly videoCategories = VideoCategoriesAPI
    public static readonly videoShows = VideoShowsAPI
    public static readonly settings = SettingsAPI
    public static readonly system = SystemAPI
}

export function validResponseData(data: ResponseData): boolean {
    return data !== undefined && data !== null && Object.keys(data).length > 0;
}