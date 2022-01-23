import axios from "axios";
import {ResponseData} from "./API";

export interface FirstTimeSetupResponseData extends ResponseData {
    api_key: string
    setup_initiated: boolean
    setup_complete: boolean
}

export interface UpdateIndexParams {
    updateType: string
}

export default class SystemAPI {
    public static getFirstTimeSetupState() {
        return axios.get<FirstTimeSetupResponseData>(`/api/system/first-time-setup-state`);
    }

    public static runFirstTimeSetup() {
        return axios.post(`/api/system/run-first-time-setup`, {});
    }

    public static updateIndex(params: UpdateIndexParams) {
        return axios.post<ResponseData>(`/api/system/update-index`, params);
    }
}