<template>
    <div>
        <h1 class="display-3 mb-5">{{ areaTitle }}</h1>
        <div class="mb-5">
            <h5 class="mb-3">System Controls</h5>
            <label class="me-3 form-label fw-500">Update Index</label>
            <small class="text-muted">Refresh the video index. A quick update pulls new videos since the last index update. A full update refreshes the full index. A full update can take several minutes.</small>
            <icon-button :click="void(0)" :icon="'lightning-fill'" :text="'Quick Update'" class="btn-outline-primary me-2"></icon-button>
            <icon-button :click="void(0)" :icon="'arrow-clockwise'" :text="'Full Update'" class="btn-outline-primary me-2"></icon-button>
        </div>
        <setting-group :group="generalGroup"></setting-group>
        <setting-group v-for="group in definedGroups" :group="group" :key="group.id"></setting-group>
        <icon-button :click="save" :icon="'check2'" :text="'Save Changes'" :class="{disabled: !modified}" class="btn-primary float-end"></icon-button>
    </div>
</template>

<script lang="ts">
import {Component} from "vue-property-decorator";
import SettingGroup from "./ts/SettingGroup";
import SettingItem from "./ts/SettingItem";
import {ISettingEntryData} from "./ts/SettingInterfaces";
import SettingGroupComponent from "./components/SettingGroupComponent.vue";
import IconButton from "../../core/components/IconButton.vue";
import GbmmVue from "../../core/ts/GbmmVue";
import API from "../../core/ts/gbmmapi/API";

@Component({
    components: {IconButton, SettingGroup: SettingGroupComponent}
})
export default class Settings extends GbmmVue {
    public settings: ISettingEntryData[] = []
    public generalGroup: SettingGroup = new SettingGroup('General')
    public definedGroups: SettingGroup[] = []

    public created() {
        this.areaTitle = 'Settings';
        this.load();
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

    public load() {
        this.generalGroup.items.length = 0

        API.settings.getAll()
            .then((response) => {
                this.settings = response.data.settings;
                let general = this.settings.filter(item => item.item);
                for (let entry of general) {
                    this.generalGroup.items.push(new SettingItem(entry.item));
                }

                let grouped = this.settings.filter(item => item.group);
                for (let entry of grouped) {
                    this.definedGroups.push(new SettingGroup(entry.group));
                }
            });
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

        API.settings
            .set({ settings: pairs })
            .then((response) => {
                this.resetModified();
            });
    }
}
</script>

<style scoped>

</style>