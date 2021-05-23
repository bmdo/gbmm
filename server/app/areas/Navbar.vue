<template>
<nav class="navbar navbar-expand-sm navbar-light bg-light">
    <div class="container-xxl">
        <div class="d-flex px-3 flex-grow-1">
            <!-- TODO index address -->
            <router-link to="/" class="navbar-brand">gbmm</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar--content">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbar--content">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li v-for="item in nav" class="nav-item">
                        <!-- TODO active link and navbar links -->
                        <router-link :to="item.path" class="nav-link">{{item.friendlyName}}</router-link>
                    </li>
                </ul>
                <ul class="navbar-nav mb-2 mb-lg-0">
                    <li class="nav-item">
                        <!-- TODO active link and settings link -->
                        <router-link to="/settings" class="nav-link">Settings</router-link>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</nav>
</template>

<script lang="ts">
import {Component} from 'vue-property-decorator';
import GbmmVue from "../core/ts/GbmmVue";

@Component({})
export default class Navbar extends GbmmVue {
    public nav = [
        {friendlyName: 'Videos', name : 'videos', path: '/videos'},
        {friendlyName: 'Downloads', name: 'downloads', path: '/downloads'}
    ]
}
</script>

<style lang="sass" scoped>

</style>