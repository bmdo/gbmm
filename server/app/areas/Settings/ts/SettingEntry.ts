import {ISettingBaseData} from "./SettingInterfaces";

export default class SettingEntry {
    private static curId = 0

    public id: number
    public name: string

    private static nextId() {
        return this.curId++;
    }

    public constructor(data: ISettingBaseData) {
        this.id = SettingEntry.nextId();
        this.name = data.name ?? '';
    }

    public get friendlyName(): string {
        if (this.name.length > 0) {
            return this.name[0].toUpperCase() + this.name.slice(1);
        }
        return ''
    }
}