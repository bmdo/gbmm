import axios from "axios";
import {ResponseData} from "./API";

export interface UpdateIndexParams {
    updateType: string
}

export default class SystemAPI {
    public static updateIndex(params: UpdateIndexParams) {
        return axios.post<ResponseData>(`/api/system/update-index`, params);
    }
}