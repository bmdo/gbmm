import Download from "./Download";
import {FileResponseData} from "./gbmmapi/FilesAPI";
import Definitions from "./Definitions";

export default class File {
    public id: number
    public objItemName: string
    public objId: number
    public objUrlField: string
    public downloads: Download[]
    public path: string
    public sizeBytes: number
    public contentType: string

    public constructor(data: FileResponseData, definitions: Definitions) {
        this.id = data.id;
        this.objItemName = data.obj_item_name;
        this.objId = data.obj_id;
        this.objUrlField = data.obj_url_field;
        if (data.downloads != null) {
            this.downloads = [];
            for (let d of data.downloads) {
                this.downloads.push(new Download(d, definitions));
            }
        }
        this.path = data.path;
        this.sizeBytes = data.size_bytes;
        this.contentType = data.content_type;
    }
}