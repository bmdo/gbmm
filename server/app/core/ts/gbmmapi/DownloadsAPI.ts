import axios from "axios";
import {FileResponseData} from "./FilesAPI";
import {MultipleResponseData, ResponseData} from "./API";

export interface DownloadResponseData extends ResponseData {
    id: number,
    name: string,
    obj_item_name: string,
    obj_id: number,
    obj_url_field: string,
    file_id: number,
    file: FileResponseData,
    status: number,
    failed_reason: string,
    created_time: string, // DateTime
    start_time: string, // DateTime
    finish_time: string, // DateTime
    url: string,
    size_bytes: number,
    downloaded_bytes: number,
    content_type: string,
    response_headers: string
}

export interface DownloadsGetFilters {
    id?: number | number[],
    obj_item_name?: string | string[],
    obj_id?: number | number[],
    status?: number | number[],
    limit?: number,
    page?: number
}

export interface DownloadEnqueueParams {
    obj_item_name: string,
    obj_id: number
}

export default class DownloadsAPI {
    public static get(filters: DownloadsGetFilters) {
        return axios.post<MultipleResponseData<DownloadResponseData>>(`/api/downloads/get`, filters);
    }

    public static getOne(filters: DownloadsGetFilters) {
        return axios.post<DownloadResponseData>(`/api/downloads/get-one`, filters);
    }

    public static enqueue(params: DownloadEnqueueParams) {
        return axios.post<DownloadResponseData>('/api/downloads/enqueue', params);
    }
}