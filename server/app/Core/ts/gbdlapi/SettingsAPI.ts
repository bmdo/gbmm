import axios from "axios";
import {ResponseData} from "./API";

export interface StartupResponseData extends ResponseData {
    api_key: string
    startup_initiated: boolean
    startup_complete: boolean
}

export interface SettingsSetItem {
    address: string
    value: string
}

export interface SettingsSetParams {
    settings: SettingsSetItem[]
}

export default class SettingsAPI {
    public static startup() {
        return axios.get<StartupResponseData>(`/api/settings/startup`);
    }

    public static set(args: SettingsSetParams) {
        return axios.post(`/api/settings/modify`, args);
    }
}