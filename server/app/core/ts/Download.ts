import Progress from './Progress';
import File from "./File";
import API, {ResponsePromise, validResponseData} from "./gbmmapi/API";
import {DownloadEnqueueParams, DownloadResponseData, DownloadsGetFilters} from "./gbmmapi/DownloadsAPI";
import Loadable from "./Loadable";
import Definitions from "./Definitions";
import ResultList from "./ResultList";

export default class Download extends Loadable {
    // Serialized fields
    public id: number = -1
    public name: string
    public objItemName: string
    public objId: number
    public objUrlField: string
    public fileId: number
    public file: File
    public status: number = 0
    public failedReason: string
    public createdTime: string
    public startTime: string
    public finishTime: string
    public url: string
    public sizeBytes: number = 0
    public downloadedBytes: number = 0
    public contentType: string
    public responseHeaders: string

    // Non-serialized fields
    public progress: Progress = new Progress()
    public valid: boolean = false
    public definitions: Definitions

    public constructor(data: DownloadResponseData, definitions: Definitions) {
        super();
        this.definitions = definitions;
        if (validResponseData(data)) {
            this.update(data);
        }
        this.loaded = true;
    }

    public static async get(filters: DownloadsGetFilters) {
        const definitions = await Definitions.get();
        const response = await API.downloads.getOne(filters);
        return new Download(response.data, definitions);
    }

    public static async getMany(filters: DownloadsGetFilters) {
        const definitions = await Definitions.get();
        const responses = await API.downloads.get(filters);
        return new ResultList(Download, responses.data, definitions);
    }

    public static async enqueue(params: DownloadEnqueueParams) {
        const definitions = await Definitions.get();
        const response = await API.downloads.enqueue(params);
        return new Download(response.data, definitions);
    }

    public update(data: DownloadResponseData) {
        if (!validResponseData(data)) return;
        this.valid = true;
        this.id = data.id;
        this.name = data.name;
        this.objItemName = data.obj_item_name;
        this.objId = data.obj_id;
        this.objUrlField = data.obj_url_field;
        if (data.file_id !== null && data.file !== null && this.fileId !== data.file_id) {
            this.fileId = data.file_id;
            this.file = new File(data.file, this.definitions);
        }
        this.status = data.status;
        this.sizeBytes = data.size_bytes;
        this.downloadedBytes = data.downloaded_bytes;
        this.createdTime = data.created_time;
        this.startTime = data.start_time;
        this.finishTime = data.finish_time;
        this.progress.update(this.sizeBytes, this.downloadedBytes);
    }

    public get statusName(): string {
        switch (this.status) {
            case this.definitions.downloadStatuses.QUEUED:
                return 'Queued';
            case this.definitions.downloadStatuses.IN_PROGRESS:
                return 'Downloading';
            case this.definitions.downloadStatuses.COMPLETE:
                return 'Complete';
            case this.definitions.downloadStatuses.PAUSED:
                return 'Paused';
            case this.definitions.downloadStatuses.CANCELLED:
                return 'Canceled';
            case this.definitions.downloadStatuses.FAILED:
                return 'Failed';
            default:
                return 'Unknown';
        }
    }

    get isQueued(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.QUEUED;
    }

    get isInProgress(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.IN_PROGRESS;
    }

    get isComplete(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.COMPLETE;
    }

    get isPaused(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.PAUSED;
    }

    get isCanceled(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.CANCELLED;
    }

    get isFailed(): boolean {
        return this.valid && this.status === this.definitions.downloadStatuses.FAILED;
    }
}

export interface DownloadFilters {
    id: number
}