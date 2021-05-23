import axios from "axios";
import {ResponseData} from "./API";

export interface DownloadStatusesResponseData {
    QUEUED: number,
    IN_PROGRESS: number,
    PAUSED: number,
    CANCELLED: number,
    COMPLETE: number,
    FAILED: number
}

export interface DefinitionsResponseData extends ResponseData {
    download_statuses: DownloadStatusesResponseData
}

export default class DefinitionsAPI {
    public static get() {
        return axios.get<DefinitionsResponseData>(`/api/definitions/get`);
    }
}