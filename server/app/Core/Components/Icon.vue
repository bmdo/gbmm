<template>
    <svg class="bi" :class="cls" :width="size_" :height="size_">
        <use :xlink:href="`${svg}#${name}`" />
    </svg>
</template>

<script lang="ts">
import GbmmVue from "../ts/GbmmVue";
import {Component, Prop} from "vue-property-decorator";
import SVG from '/node_modules/bootstrap-icons/bootstrap-icons.svg'

@Component({})
export default class Icon extends GbmmVue {
    @Prop()
    public name: string
    @Prop()
    public size: string
    @Prop()
    public cls: object

    public svg = SVG

    private size_: string

    created() {
        if (this.size === null || this.size === undefined || this.size === '') {
            this.size_ = '1rem';
        }
        else {
            this.size_ = this.size;
        }
    }
}
</script>

<style lang="sass" scoped>
svg
  fill: currentColor
</style>