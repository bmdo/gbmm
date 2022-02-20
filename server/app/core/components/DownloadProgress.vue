<template>
  <div class="download-progress">
    <div class="d-flex align-items-center">
        <div class="spinner-border download-spinner" role="status"></div>
        <span class="fw-500 mx-2">Downloading</span>
        <span class="download-percent mx-2 fw-500">{{ download.progress.percentString }}</span>
        <small class="mx-2 text-muted">{{ download.progress.rateString }}</small>
    </div>
    <div class="progress download-progress mt-2">
        <div class="progress-bar" role="progressbar" :style="{ width: download.progress.percentString }"></div>
    </div>
  </div>
</template>

<script lang="ts">
import {Component, Prop} from "vue-property-decorator";
import Download from '../ts/Download';
import SubscriberVue from "../ts/Subscriber";
import {Message} from "../ts/gbmmapi/SubscriptionsAPI";

@Component({})
export default class DownloadProgress extends SubscriberVue {
    @Prop()
    public download!: Download

    public created() {
        this.addInterest('Download');
    }

    public async receive_message(message: Message) {
        this.download.update(message.data);
    }
}
</script>

<style lang="sass" scoped>
.download-progress
  flex: 1

  .download-spinner
    display: inline-block
    width: 0.75rem
    height: 0.75rem
    border-width: thin
    vertical-align: middle
    border-top-color: transparent
    animation-duration: 0.25s

  .download-progress
    height: 3px

  .download-percent
    width: 2rem
</style>