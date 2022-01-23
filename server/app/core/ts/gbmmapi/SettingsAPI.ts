import axios from "axios";
import {ResponseData} from "./API";

export interface StartupResponseData extends ResponseData {
    api_key: string
    startup_initiated: boolean
    startup_complete: boolean
}

export interface SettingsResponseData extends ResponseData {
    settings: SettingsGroupWrapper[]
}

export interface SettingsGroupWrapper {
    group: SettingsGroup
}

export interface SettingsGroup {
    address: string
    items: SettingsItemWrapper[]
    name: string
}

export interface SettingsItemWrapper {
    item: SettingsItem
}

export interface SettingsItem {
    address: string
    helptext: string
    name: string
    type: string
    value: string
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

    public static getAll() {
        return axios.get<SettingsResponseData>(`/api/settings/get-all`);
    }

    public static set(args: SettingsSetParams) {
        return axios.post(`/api/settings/modify`, args);
    }

    public static updateIndex(args: SettingsSetParams) {
        return axios.post(`/api/settings/modify`, args);
    }
}