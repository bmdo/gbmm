<template>
    <div class="mb-3">
        <label class="me-3 form-label">{{item.friendlyName}}</label>
        <small class="text-muted">{{item.helptext}}</small>
        <input-text :model="item.model"></input-text>
    </div>
</template>

<script lang="ts">
import GbmmVue from "../../../core/ts/GbmmVue";
import {Component, Prop} from "vue-property-decorator";
import SettingItem from "../ts/SettingItem";
import InputText from "../../../core/components/InputText.vue";

@Component({
    components: {InputText}
})
export default class SettingItemComponent extends GbmmVue {
    @Prop()
    item: SettingItem
}
</script>

<style lang="sass" scoped>

</style>