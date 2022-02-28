import axios from "axios";
import {ResponseData} from "./API";

export interface FirstTimeSetupResponseData extends ResponseData {
    api_key: string,
    setup_initiated: boolean,
    setup_complete: boolean
}

export enum IndexerState {
    NotStarted = 0,
    Running = 1,
    Paused = 2,
    Complete = 3,
    Stopped = 4,
    Failed = 5
}

export interface IndexerStateResponseData extends ResponseData {
    active: boolean,
    uuid: string,
    type: 'quick' | 'full',
    state: IndexerState,
    progress_current: number,
    progress_denominator: number,
    last_update: string // DateTime
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

    public static getIndexerState() {
        return axios.get<IndexerStateResponseData>(`/api/system/get-indexer-state`);
    }
}