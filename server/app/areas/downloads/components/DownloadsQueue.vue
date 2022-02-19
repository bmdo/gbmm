<template>
    <div>
        <div class="my-5">
            <h5>In Progress<span class="badge bg-light text-primary ms-3 mb-4">{{vm.downloadsInProgress.length}}</span></h5>
            <div v-for="d in vm.downloadsInProgress" :key="d.id" class="mb-3 p-3 bg-light">
                <h5 class="fw-500 mb-3">{{d.name}}</h5>
                <download-progress :download="d"></download-progress>
            </div>

            <p v-if="vm.downloadsInProgress.length === 0">No downloads in progress.</p>
        </div>
        <div class="my-5">
            <div class="d-flex align-items-center">
                <h5 class="flex-grow-1">Queue<span class="badge bg-light text-primary ms-3">{{vm.totalResults}}</span></h5>
                <nav>
                    <ul class="pagination">
                        <li v-for="pageNum in pageNumbers" class="page-item" :class="{active: vm.page === pageNum}"><router-link :to="`/downloads/queue/${pageNum}`" class="page-link">{{pageNum}}</router-link></li>
                    </ul>
                </nav>
            </div>
            <downloads-queue-table :downloads="vm.downloadsInQueue"></downloads-queue-table>
            <p v-if="vm.downloadsInQueue.length === 0" class="text-center">Nothing in the queue. Go download something!</p>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Watch} from 'vue-property-decorator';
import GbmmVue from "../../../core/ts/GbmmVue";
import Download from "../../../core/ts/Download";
import DownloadsQueueTable from "./DownloadsQueueTable.vue";
import Definitions from "../../../core/ts/Definitions";
import DownloadProgress from "../../../core/components/DownloadProgress.vue";
import ResultList from "../../../core/ts/ResultList";

interface DownloadsQueueVM {
    downloadsInProgress: ResultList<Download>,
    downloadsInQueue: ResultList<Download>,
    limit: number,
    page: number,
    totalPages: number,
    totalResults: number
}

@Component({
    components: {DownloadProgress, DownloadsQueueTable}
})
export default class DownloadsQueue extends GbmmVue {
    private interval: number

    public vm: DownloadsQueueVM = {
        downloadsInProgress: new ResultList(),
        downloadsInQueue: new ResultList(),
        limit: 20,
        page: 1,
        totalPages: 0,
        totalResults: 0
    }

    public get pageNumbers() {
        return Array.from({length: this.vm.totalPages}, (v, k) => k + 1);
    }

    public created() {
        this.load();
        // TODO add subscriber
    }

    public async load() {
        let definitions = await Definitions.get();
        this.vm.downloadsInProgress = await Download.getMany({
            status: [
                definitions.downloadStatuses.IN_PROGRESS
            ]
        })
        this.vm.downloadsInQueue = await Download.getMany({
            status: [
                definitions.downloadStatuses.QUEUED,
                definitions.downloadStatuses.PAUSED
            ],
            limit: this.vm.limit,
            page: this.vm.page
        })
        this.vm.page = this.vm.downloadsInQueue.metadata.current_page;
        this.vm.totalPages = this.vm.downloadsInQueue.metadata.total_pages;
        this.vm.totalResults = this.vm.downloadsInQueue.metadata.total_results;
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