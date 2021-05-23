<template>
    <div>
        <div class="d-flex align-items-center">
            <h1 class="display-3">Downloads</h1>
            <ul class="nav nav-pills mx-5">
                <li v-for="item in downloads_routes" class="nav-item">
                    <router-link :to="item.meta.navPath" :class="{active: item.meta.active}" class="nav-link">{{item.meta.friendlyName}}</router-link>
                </li>
            </ul>
        </div>
        <router-view></router-view>
    </div>
</template>

<script lang="ts">
import {Component, Watch} from 'vue-property-decorator';
import GbmmVue from "../../core/ts/GbmmVue";

@Component({})
export default class Downloads extends GbmmVue {
    public downloads_routes = this.$router.options.routes.find(r => r.name === 'downloads')?.children.filter(r => r.meta?.navPath);

    public created() {
        this.areaTitle = 'Downloads';
        this.setActive();
    }

    @Watch('$route')
    public onRouteChange = (to: string, from: string) => {
        this.setActive();
    }

    public setActive = () => {
        for (let r of this.downloads_routes) {
            r.meta.active = (this.$route.path.indexOf(r.meta.navPath) >= 0);
        }
    }
}
</script>

<style lang="sass" scoped>

</style>