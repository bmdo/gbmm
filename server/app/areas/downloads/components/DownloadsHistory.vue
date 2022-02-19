<template>
    <div class="my-5">
        <div class="d-flex align-items-center">
            <h5 class="flex-grow-1">History<span class="badge bg-light text-primary ms-3">{{vm.totalResults}}</span></h5>
            <nav>
                <ul class="pagination">
                    <li v-for="pageNum in pageNumbers" class="page-item" :class="{active: vm.page === pageNum}"><router-link :to="`/downloads/history/${pageNum}`" class="page-link">{{pageNum}}</router-link></li>
                </ul>
            </nav>
        </div>
        <downloads-history-table :downloads="vm.downloads"></downloads-history-table>
        <p v-if="vm.downloads.length === 0" class="text-center">Nothing in the history. Go download something!</p>
    </div>
</template>

<script lang="ts">
import {Component, Watch} from 'vue-property-decorator';
import GbmmVue from "../../../core/ts/GbmmVue";
import Download from "../../../core/ts/Download";
import DownloadsHistoryTable from "./DownloadsHistoryTable.vue";
import Definitions from "../../../core/ts/Definitions";
import ResultList from "../../../core/ts/ResultList";

interface DownloadsHistoryVM {
    downloads: ResultList<Download>,
    limit: number,
    page: number,
    totalPages: number,
    totalResults: number
}

@Component({
    components: {DownloadsHistoryTable}
})
export default class DownloadsHistory extends GbmmVue {
    public vm: DownloadsHistoryVM = {
        downloads: new ResultList<Download>(),
        limit: 20,
        page: parseInt(this.$route.params.page ?? '1'),
        totalPages: 0,
        totalResults: 0
    }

    public get pageNumbers() {
        return Array.from({length: this.vm.totalPages}, (v, k) => k + 1);
    }

    public created() {
        this.load();
        // TODO add subscriber (maybe in Downloads.vue instead?)
    }

    public async load() {
        let definitions = await Definitions.get();
        this.vm.downloads = await Download.getMany({
            status: [
                definitions.downloadStatuses.COMPLETE,
                definitions.downloadStatuses.CANCELLED,
                definitions.downloadStatuses.FAILED
            ],
            limit: this.vm.limit,
            page: this.vm.page
        })
        this.vm.page = this.vm.downloads.metadata.current_page
        this.vm.totalPages = this.vm.downloads.metadata.total_pages
        this.vm.totalResults = this.vm.downloads.metadata.total_results
    }

    @Watch('$route')
    public onRouteChange = (to: string, from: string) => {
        this.vm.page = parseInt(this.$route.params.page ?? '1');
        this.load();
    }
}
</script>

<style lang="sass" scoped>

</style>