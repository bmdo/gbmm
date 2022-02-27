import {ISettingItemData} from "./SettingInterfaces";
import SettingEntry from "./SettingEntry";
import InputModel from "../../../core/ts/InputModel";

export default class SettingItem extends SettingEntry {
    public address: string = ''
    public helptext: string = ''
    public model: InputModel<string> = null

    public constructor(data: ISettingItemData) {
        super(data);
        this.address = data.address;
        this.helptext = data.helptext;
        this.model = new InputModel<string>(data.value);
    }

    public get modified() {
        return this.model.modified;
    }
}