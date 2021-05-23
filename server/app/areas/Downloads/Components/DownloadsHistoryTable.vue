<template>
    <table class="table">
        <thead>
            <tr>
                <th>Status</th>
                <th>Type</th>
                <th>Name</th>
                <th>Completed at</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="download in downloads">
                <td>{{download.statusName}}</td>
                <td>{{download.objItemName}}</td>
                <td>{{download.name}}</td>
                <td>{{download.finishTime}}</td>
            </tr>
        </tbody>
    </table>
</template>

<script lang="ts">
import {Component, Prop} from 'vue-property-decorator';
import Downloads from "../Downloads.vue";
import GbmmVue from "../../../core/ts/GbmmVue";

@Component({})
export default class DownloadsTable extends GbmmVue {
    @Prop()
    downloads: Downloads[]
}
</script>

<style lang="sass" scoped>

</style>