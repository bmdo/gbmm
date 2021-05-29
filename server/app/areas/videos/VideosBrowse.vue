<template>
    <div :class="{'select-mode': vm.selectMode}">
        <div class="header">
            <div v-if="!vm.selectMode" class="header-normal">
                <h1 class="display-3 mb-0 flex-grow-1">Video Browser</h1>
                <icon-button :click="toggleSelectMode" :icon="'grid-fill'" :text="'Select'" class="btn-outline-primary me-3"></icon-button>
            </div>
            <div v-else class="header-select bg-dark rounded p-3">
                <div class="flex-grow-1">
                    <span class="fw-700 text-light">{{vm.selected.length}}</span>
                    <span class="fw-500 text-light">Selected</span>
                </div>
                <icon-button :click="downloadSelected" :icon="'download'" :text="'Download selected'" class="btn-outline-light"></icon-button>
                <span class="ps-4 me-4 border-end align-self-stretch"></span>
                <icon-button :click="toggleSelectAll" :icon="'check-all'" :text="'Select all'" class="btn-outline-light me-2"></icon-button>
                <icon-button :click="toggleSelectMode" :icon="'x-lg'" :text="'Close select'" class="btn-outline-light"></icon-button>
            </div>
        </div>
        <div class="d-flex">
            <videos-filter-panel :filters="filters" :sort="sortOptions" :filter-callback="onFilterApply"></videos-filter-panel>
            <div class="flex-grow-1">
                <div class="container-fluid g-0">
                    <div class="row gy-4">
                        <div v-for="video in videos" class="col-sm-6 col-md-4 col-lg-3">
                            <div class="ratio ratio-1x1">
                                <div @click="() => { toggleSelect(video.id) }" class="card video-card" :class="{selected: vm.selected.filter(i => i === video.id).length > 0}">
                                    <icon v-if="vm.selected.filter(i => i === video.id).length > 0" :name="'check-circle-fill'" :size="'2rem'" class="select-icon"></icon>
                                    <icon v-else :name="'circle'" :size="'2rem'" class="select-icon"></icon>
                                    <img :src="video.image.medium_url" class="card-img-top" />
                                    <div class="card-body overflow-hidden position-relative">
                                        <span class="card-title fw-500">{{video.name}}</span>
                                        <div v-if="video.download != null && !video.download.isFailed && !video.download.isCanceled" class="download-indicator rounded-bottom text-light">
                                            <div v-if="video.download.isInProgress" class="d-flex align-items-center">
                                                <div class="spinner-border download-spinner" role="status"></div>
                                                <small class="fw-500 ms-1">Downloading</small>
                                            </div>
                                            <div v-if="video.download.isComplete" class="d-flex align-items-center">
                                                <icon :name="'check2'"></icon>
                                                <small class="fw-500 ms-1">Downloaded</small>
                                            </div>
                                            <div v-if="video.download.isQueued" class="d-flex align-items-center">
                                                <icon :name="'hourglass-split'"></icon>
                                                <small class="fw-500 ms-1">Queued</small>
                                            </div>
                                        </div>
                                    </div>
                                    <router-link v-if="!vm.selectMode" :to="`/videos/detail/${video.id}`" class="stretched-link"></router-link>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex justify-content-center py-5">
                        <div class="px-3">
                            <router-link :to="`/videos/browse/${this.prevPage}`" :class="{ disabled: page === 1 }" class="btn btn-link">
                                <icon :name="'arrow-left-circle'" :size="'2rem'"></icon>
                            </router-link>
                        </div>
                        <div class="d-flex align-items-center">
                            <span>Page {{this.page}}</span>
                        </div>
                        <div class="px-3">
                            <router-link :to="`/videos/browse/${this.nextPage}`" class="btn btn-link">
                                <icon :name="'arrow-right-circle'" :size="'2rem'"></icon>
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Watch} from "vue-property-decorator";
import Icon from "../../core/components/Icon.vue";
import Video from "../../core/ts/Video";
import GbmmVue from "../../core/ts/GbmmVue";
import VideosFilterPanel from "./components/VideosFilterPanel.vue";
import FilterCollection from "../../core/ts/FilterCollection";
import {VideosBrowseFilters} from "../../core/ts/gbmmapi/VideosAPI";
import {SortOption} from "../../core/ts/Sort";
import IconButton from "../../core/components/IconButton.vue";
import Download from "../../core/ts/Download";

interface VideosBrowseVM {
    selectMode: boolean,
    selected: number[],
    downloads: Download[]
}

@Component({
    components: {IconButton, VideosFilterPanel, Icon}
})
export default class VideosBrowse extends GbmmVue {
    public videos: Video[] = []
    public filters: FilterCollection = new FilterCollection()
    public sortOptions: SortOption[] = [
        {
            id: 0,
            friendlyName: 'Newest first',
            field: 'publish_date',
            direction: 'desc',
            active: true
        },
        {
            id: 1,
            friendlyName: 'Oldest first',
            field: 'publish_date',
            direction: 'asc',
            active: false
        }
    ]
    public vm: VideosBrowseVM = {
        selectMode: false,
        selected: [],
        downloads: []
    }

    public get page() { return parseInt(this.$route.params.page ?? '1') }
    public get prevPage() { return (this.page > 1) ? this.page - 1 : 1; }
    public get nextPage() { return (this.page < 1000) ? this.page + 1 : 1000; }

    public created() {
        this.areaTitle = 'Video Browser';
        this.load();
    }

    public reload = () => {
        this.clear();
        this.load();
    }

    public clear = () => {
        this.videos.length = 0;
        this.vm.selected = [];
        this.vm.selectMode = false;
    }

    public load = () => {
        let requestFilters: VideosBrowseFilters = this.filters.dumpModified();
        requestFilters.page = this.page;
        let activeSort = this.sortOptions.filter(v => v.active);
        if (activeSort.length > 0) {
            requestFilters.sort_field = activeSort[0].field;
            requestFilters.sort_direction = activeSort[0].direction;
        }
        Video.getBrowse(requestFilters).then(v => this.videos.push(...v));
    }

    public onFilterApply = () => {
        this.reload();
    }

    @Watch('$route')
    public onRouteChange = (to: string, from: string) => {
        this.reload();
    }

    public toggleSelectMode() {
        this.vm.selectMode = !this.vm.selectMode;
        this.vm.selected = [];
    }

    public toggleSelect(videoId: number) {
        if (this.vm.selectMode) {
            let ix = this.vm.selected.indexOf(videoId);
            if (ix !== -1) {
                this.vm.selected.splice(ix, 1);
            }
            else {
                this.vm.selected.push(videoId);
            }
        }
    }

    public toggleSelectAll() {
        if (this.vm.selectMode) {
            if (this.vm.selected.length !== this.videos.length) {
                // Select all
                this.vm.selected.length = 0;
                for (let v of this.videos) {
                    this.vm.selected.push(v.id);
                }
            }
            else {
                // Deselect all
                this.vm.selected = [];
            }
        }
    }

    public downloadSelected = () => {
        if (this.vm.selectMode) {
            for (let id of this.vm.selected) {
                let video = this.videos.filter(v => v.id === id)[0];
                if (video.download == null || (!video.download.isInProgress && !video.download.isQueued && !video.download.isPaused && !video.download.isComplete)) {
                    this.enqueue_download(id);
                }
            }
            this.toggleSelectMode();
        }
    }

    public enqueue_download(id: number) {
        Download.enqueue({obj_item_name: 'video', obj_id: id}).then(d => this.vm.downloads.push(d));
    }
}

</script>

<style lang="sass" scoped>
@use '../../core/core' as core
#filters
  width: 16rem

.header
  height: 4rem
  display: flex
  margin-bottom: 2rem

.header-normal
  display: flex
  width: 100%
  align-items: center

.header-select
  display: flex
  width: 100%
  align-items: center

.card:hover
  border: 1px solid core.$gray-600

.card-body
  line-height: 1

.download-indicator
  display: flex
  align-items: center
  justify-content: center
  background: core.$primary
  position: absolute
  bottom: 0
  left: 0
  right: 0
  line-height: 1
  height: 1.25rem

.select-icon
  display: none
  position: absolute
  top: 1rem
  left: 1rem
  background: white
  padding: 0.1rem
  border-radius: 1000px

.select-mode
  .select-icon
    display: block

  .card
    opacity: 0.4

    &:hover
      opacity: 1
      cursor: pointer

    &:hover:after
      content: ''
      position: absolute
      top: -4px
      left: -4px
      right: -4px
      bottom: -4px
      border: 2px solid core.$primary
      border-radius: 0.35rem

    &.selected
      opacity: 1
      cursor: pointer

    &.selected:after
      content: ''
      position: absolute
      top: -7px
      left: -7px
      right: -7px
      bottom: -7px
      border: 5px solid core.$primary
      border-radius: 0.5rem

.download-spinner
  display: inline-block
  width: 0.75rem
  height: 0.75rem
  border-width: thin
  vertical-align: middle
  border-top-color: transparent
  animation-duration: 0.25s

</style>