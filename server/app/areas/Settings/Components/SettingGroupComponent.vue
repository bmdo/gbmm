<template>
    <div class="mb-5" v-if="group.items.length > 0 || group.subgroups.length > 0">
        <h5 class="mb-3">{{group.friendlyName}}</h5>
        <setting-item v-for="item in group.items" :item="item" :key="item.id"></setting-item>
        <setting-group v-for="subgroup in group.subgroups" :group="subgroup" :key="subgroup.id"></setting-group>
    </div>
</template>

<script lang="ts">
import GbmmVue from "../../../core/ts/GbmmVue";
import {Component, Prop} from "vue-property-decorator";
import SettingGroup from "../ts/SettingGroup";
import SettingItemComponent from "./SettingItemComponent.vue";

@Component({
    components: {
        SettingItem: SettingItemComponent,
        SettingGroup: SettingGroupComponent
    }
})
export default class SettingGroupComponent extends GbmmVue {
    @Prop()
    public group: SettingGroup
}
</script>

<style lang="sass" scoped>

</style>