import axios from "axios";
import {ResponseData} from "./API";

export interface StartupResponseData extends ResponseData {
    api_key: string
    startup_initiated: boolean
    startup_complete: boolean
}

export interface UpdateIndexParams {
    updateType: string
}

export default class SystemAPI {
    public static getFirstTimeStartupState() {
        return axios.get<StartupResponseData>(`/api/system/first-time-startup-state`);
    }

    public static runFirstTimeStartup() {
        return axios.post(`/api/system/run-first-time-startup`, {});
    }

    public static updateIndex(params: UpdateIndexParams) {
        return axios.post<ResponseData>(`/api/system/update-index`, params);
    }
}