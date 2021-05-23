<template>
  <div class="d-flex">
    <div>
      <span>{{download.id}}</span>
    </div>
  </div>
</template>

<script lang="ts">
import {Component, Prop} from "vue-property-decorator";
import Download from '../ts/Download';
import GbmmVue from "../ts/GbmmVue";

@Component({})
export default class DownloadQueueEntry extends GbmmVue {
  @Prop()
  public download!: Download
}
</script>

<style lang="sass" scoped>

</style>