<template>
    <div>
        <h1 class="display-3 mb-5">{{ title }}</h1>
        <setting-group :group="generalGroup"></setting-group>
        <setting-group v-for="group in definedGroups" :group="group" :key="group.id"></setting-group>
        <button class="btn fw-500 w-100" @click="save" :class="{disabled: !modified}">Save</button>
    </div>
</template>

<script lang="ts">
import {Component} from "vue-property-decorator";
import axios from "axios";
import SettingGroup from "./ts/SettingGroup";
import SettingItem from "./ts/SettingItem";
import {ISettingEntryData} from "./ts/SettingInterfaces";
import SettingGroupComponent from "./components/SettingGroupComponent.vue";
import GbmmVue from "../../core/ts/GbmmVue";

@Component({
    components: {SettingGroup: SettingGroupComponent}
})
export default class Settings extends GbmmVue {
    public settings: ISettingEntryData[] = []
    public generalGroup: SettingGroup = new SettingGroup('General')
    public definedGroups: SettingGroup[] = []

    public created() {
        this.areaTitle = 'Settings';
        let general = this.settings.filter(item => item.item)
        for (let entry of general) {
            this.generalGroup.items.push(new SettingItem(entry.item))
        }

        let grouped = this.settings.filter(item => item.group)
        for (let entry of grouped) {
            this.definedGroups.push(new SettingGroup(entry.group))
        }
    }

    public get modified(): boolean {
        return this.generalGroup.modified || this.definedGroups.filter(group => group.modified).length > 0;
    }

    public resetModified() {
        this.generalGroup.resetModified();
        for (let group of this.definedGroups) {
            group.resetModified();
        }
    }

    public save() {
        let items = this.generalGroup.getModifiedItems()
        for (let group of this.definedGroups) {
            items = items.concat(group.getModifiedItems())
        }

        let pairs = items.map((item) => {
            return {
                address: item.address,
                value: item.model.value
            };
        });

        axios
            .post('/settings/modify', {
                settings: pairs
            })
            .then((response) => {
                this.resetModified();
            })
    }
}
</script>

<style scoped>

</style>