import {ISettingGroupData} from "./SettingInterfaces";
import SettingItem from "./SettingItem";
import SettingEntry from "./SettingEntry";

export default class SettingGroup extends SettingEntry {
    public items: SettingItem[]
    public subgroups: SettingGroup[]

    public constructor(data: ISettingGroupData | string) {
        if (typeof data === 'string') {
            data = {
                name: data,
                items: []
            }
        }
        super(data);

        this.items = [];
        this.subgroups = [];

        for (let item of data.items) {
            if (item.group) {
                this.subgroups.push(new SettingGroup(item.group))
            }
            else if (item.item) {
                this.items.push(new SettingItem(item.item))
            }
        }
    }

    public get modified(): boolean {
        return this.getModifiedItems().length > 0;
    }

    public resetModified() {
        for (let item of this.items) {
            item.model.resetModified();
        }
        for (let group of this.subgroups) {
            group.resetModified();
        }
    }

    public getModifiedItems(): SettingItem[] {
        let items = this.items.filter(item => item.modified);
        for (let group of this.subgroups) {
            items = items.concat(group.getModifiedItems());
        }
        return items;
    }
}