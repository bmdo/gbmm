import {DownloadResponseData} from "./DownloadsAPI";
import {ResponseData} from "./API";

export interface FileResponseData extends ResponseData {
    id: number
    obj_item_name: string
    obj_id: number
    obj_url_field: string
    downloads?: DownloadResponseData[]
    path: string
    size_bytes: number
    content_type: string
}

export default class FilesAPI {

}