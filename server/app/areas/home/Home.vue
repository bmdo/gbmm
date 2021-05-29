<template>
<p>Welcome Home</p>
</template>

<script lang="ts">
import {Component} from 'vue-property-decorator';
import GbmmVue from "../../core/ts/GbmmVue";

@Component({})
export default class Home extends GbmmVue {

    created() {
        this.areaTitle = 'Home';
    }

}
</script>

<style lang="sass" scoped>

</style>