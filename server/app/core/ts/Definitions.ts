import DownloadStatuses from "./DownloadStatuses";
import {DefinitionsResponseData} from "./gbdlapi/DefinitionsAPI";
import API, {ResponsePromise, validResponseData} from "./gbdlapi/API";

export default class Definitions {
    public downloadStatuses: DownloadStatuses

    private static loading: boolean = false
    private static promise: Promise<Definitions> = null
    private _loaded: boolean = false
    private _loadFailed: boolean = false

    private constructor(data: DefinitionsResponseData) {
        if (!validResponseData(data)) {
            this.loadFailed = true;
            return;
        }
        this.downloadStatuses = new DownloadStatuses(data.download_statuses);
        this.loaded = true;
    }

    public static async get(): Promise<Definitions> {
        if (Definitions.promise == null) {
            Definitions.promise = Definitions.load();
        }
        return this.promise;
    }

    public get loaded(): boolean {
        return this._loaded;
    }

    public set loaded(value: boolean) {
        this._loaded = value;
    }

    public get loadFailed(): boolean {
        return this._loadFailed;
    }

    public set loadFailed(value: boolean) {
        this._loadFailed = value;
    }

    private static load() {
        Definitions.loading = true;
        return API.definitions.get().then(r => new Definitions(r.data));
    }
}