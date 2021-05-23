export default class Loadable {
    public _loaded: boolean = false;
    public loadFailed: boolean = false;

    public get loaded(): boolean {
        return this._loaded && !this.loadFailed;
    }

    public set loaded(l: boolean) {
        this._loaded = true;
    }
}

