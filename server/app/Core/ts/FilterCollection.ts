export default class FilterCollection {
    public checkbox = new Array<CheckboxFilter>()
    public radio = new Array<RadioFilter>()

    public get all(): Array<Filter> {
        return []
            .concat(this.checkbox)
            .concat(this.radio);
    }

    public addCheckbox(filter: CheckboxFilter) {
        this.checkbox.push(filter);
    }

    public addRadio(filter: RadioFilter) {
        this.radio.push(filter);
        this.radio.sort((a, b) => a.sort - b.sort)
    }

    public dumpModified() {
        let obj: {[k: string]: any | any[]} = {}
        for (let filter of this.all) {
            let dumpedItems = filter.dumpModified();
            if (dumpedItems != null) {
                obj[filter.name] = dumpedItems;
            }
        }
        return obj;
    }


}

export abstract class Filter {
    id: string
    name: string
    friendlyName: string
    sort: number

    constructor(args: {id: string, name: string, friendlyName: string, sort: number}) {
        this.id = args.id;
        this.name = args.name;
        this.friendlyName = args.friendlyName;
        this.sort = args.sort;
    }

    public abstract dumpModified(): null | string | string[];
}

abstract class CheckboxFilterBase extends Filter {
    items: CheckboxFilterItem[] = []

    public add(item: CheckboxFilterItem | FilterItemParams) {
        let checkboxItem: CheckboxFilterItem
        if (item instanceof CheckboxFilterItem) {
            checkboxItem = item;
        }
        else {
            checkboxItem = new CheckboxFilterItem(item);
        }
        this.items.push(checkboxItem);
    }
}

export class CheckboxFilter extends CheckboxFilterBase {
        public dumpModified() {
        let list: string[] = [];
        for (let item of this.items) {
            if (item.checked) {
                list.push(item.value);
            }
        }
        if (list.length === 0) {
            return null;
        }
        return list;
    }
}

export class RadioFilter extends CheckboxFilterBase {
    picked: string

    public dumpModified() {
        if (this.picked != null && this.picked != '') {
            return this.picked;
        }
        else {
            return null;
        }
    }
}

export interface FilterItemParams {
    id: string
    value: string
    friendlyName: string
}

export class FilterItem {
    id: string
    value: string
    friendlyName: string

    public constructor(args: FilterItemParams) {
        this.id = args.id;
        this.value = args.value;
        this.friendlyName = args.friendlyName;
    }
}

export class CheckboxFilterItem extends FilterItem {
    checked: boolean = false
}