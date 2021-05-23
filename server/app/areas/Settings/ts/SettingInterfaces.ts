export interface ISettingBaseData {
    name: string
}

export interface ISettingGroupData extends ISettingBaseData {
    items: ISettingEntryData[]
}

export interface ISettingItemData extends ISettingBaseData {
    address: string
    helptext: string
    value: string
}

export interface ISettingEntryData {
  group?: ISettingGroupData
  item?: ISettingItemData
}