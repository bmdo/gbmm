<template>
    <div v-if="loaded_(vm.video, vm.download)">
        <img :src="vm.video.image.screen_large_url" class="w-100"/>
        <div class="video-action-bar">
            <a v-if="!vm.download.valid" v-on:click="enqueue_download()" id="download" class="btn btn-primary" href="#">
                <span class="fw-500">Download</span>
                <icon :name="'download'"></icon>
            </a>
            <span v-else-if="vm.download.isQueued">
                <icon :name="'hourglass'" :size="'1.5rem'" :class="'mr-2'"></icon>
                <span class="fw-500 align-middle">Queued for download</span>
            </span>
            <span v-else-if="vm.download.isComplete">
                <icon :name="'check2'" :size="'1.5rem'" :class="'mr-2'"></icon>
                <span class="fw-500 align-middle">Downloaded</span>
            </span>
            <span v-else-if="vm.download.isFailed">
                <icon :name="'exclamation-circle'" :size="'1.5rem'" :class="'mr-2'"></icon>
                <span class="fw-500 align-middle">Download failed</span>
                <a v-on:click="enqueue_download()" id="try-again" class="btn btn-primary ms-4" href="#">
                    <span class="fw-500">Try again</span>
                    <icon :name="'arrow-clockwise'"></icon>
                </a>
            </span>
            <download-progress v-else-if="vm.download.isInProgress" v-bind:download="vm.download"></download-progress>
        </div>
        <div class="video-info py-3">
            <h1 class="display-6">{{vm.video.name}}</h1>
            <p>{{vm.video.deck}}</p>
        </div>
    </div>
</template>

<script lang="ts">
import {Component} from 'vue-property-decorator';
import Icon from "../../core/components/Icon.vue";
import Download from "../../core/ts/Download";
import Video from "../../core/ts/Video";
import DownloadProgress from "../../core/components/DownloadProgress.vue";
import GbmmVue from "../../core/ts/GbmmVue";

@Component({
    components: {
        Icon,
        DownloadProgress
    }
})
export default class VideosDetail extends GbmmVue {
    public id: number = parseInt(this.$route.params.id)
    public vm: VideosDetailVM = {
        download: null,
        video: null
    }

    public created() {
        this.areaTitle = 'Video';
        this.load();
    }

    public async load() {
        this.vm.video = await Video.get({id: this.id});
        this.vm.download = await Download.get({obj_item_name: 'video', obj_id: this.id}, true)
        this.pageTitle = this.vm.video?.name;
    }

    public enqueue_download = () => {
        Download.enqueue({obj_item_name: 'video', obj_id: this.vm.video.id}, true).then(d => this.vm.download = d);
    }
}

interface VideosDetailVM {
    download: Download,
    video: Video
}

</script>

<style lang="sass" scoped>
.video-action-bar
  display: flex
  align-items: center
  height: 4rem
  border-bottom: 1px solid #ddd
</style>