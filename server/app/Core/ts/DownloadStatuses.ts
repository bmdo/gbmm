import {DownloadStatusesResponseData} from "./gbdlapi/DefinitionsAPI";

export default class DownloadStatuses {
    public QUEUED: number
    public IN_PROGRESS: number
    public PAUSED: number
    public CANCELLED: number
    public COMPLETE: number
    public FAILED: number

    public constructor(data: DownloadStatusesResponseData) {
        this.QUEUED = data.QUEUED;
        this.IN_PROGRESS = data.IN_PROGRESS;
        this.PAUSED = data.PAUSED;
        this.CANCELLED = data.CANCELLED;
        this.COMPLETE = data.COMPLETE;
        this.FAILED = data.FAILED;
    }
}