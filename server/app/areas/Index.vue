<template>
    <div>
        <div v-if="allComplete" id="index">
            <navbar></navbar>
            <div class="container-xxl my-4">
                <div class="page px-3">
                    <router-view></router-view>
                </div>
            </div>
            <footer></footer>
        </div>
        <div v-else-if="vm.needApiKey">
            <welcome :needApiKey="vm.needApiKey" :complete-callback="onApiKeySubmitted"></welcome>
        </div>
        <div v-else-if="!vm.startupComplete" class="init-shield">
            <h1 class="display-1">gbmm</h1>
            <div v-if="!vm.initFailed" class="d-flex flex-column align-items-center">
                <span class="spinner-border init-spinner my-4"></span>
                <span class="my-4">Performing first time setup</span>
            </div>
            <div v-else class="d-flex flex-column align-items-center">
                <icon class="text-danger" :name="'exclamation-circle'" :size="'3rem'"></icon>
                <span class="my-4 text-danger">Setup failed</span>
            </div>

        </div>
        <div v-else>
            <p>Something went wrong. Try refreshing the page.</p>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Watch} from "vue-property-decorator";
import Navbar from "./Navbar.vue";
import Footer from "./Footer.vue";
import GbmmVue from "../core/ts/GbmmVue";
import API from "../core/ts/gbmmapi/API";
import Welcome from "./welcome/Welcome.vue";
import Icon from "../core/components/Icon.vue";

@Component({
    components: {
        Welcome,
        Navbar,
        Footer,
        Icon
    }
})
export default class Index extends GbmmVue {
    public vm = {
        startupChecked: false,
        needApiKey: true,
        startupInitiated: false,
        startupComplete: false,
        startupFailed: false
    }

    public waitInterval: number = -1

    public get allComplete() {
        return !this.vm.needApiKey && this.vm.startupComplete;
    }


    public created() {
        this.checkStartup();
    }

    @Watch('$route')
    public onRouteChanged(to: string, from: string) {
        this.checkStartup();
    }

    public onApiKeySubmitted() {
        this.vm.needApiKey = false;
        this.runStartup();
    }

    public async checkStartup() {
        if (!this.allComplete) {
            let startupInfo = await API.system.getFirstTimeStartupState();
            let apiKey = startupInfo.data.api_key;
            this.vm.startupInitiated = startupInfo.data.startup_initiated;
            this.vm.startupComplete = startupInfo.data.startup_complete;
            if (apiKey != null && apiKey != '') {
                this.vm.needApiKey = false;
            }
            this.vm.startupChecked = true;

            if (!this.vm.needApiKey && !this.vm.startupInitiated) {
                // For some reason, we have an API key but startup was not initiated. Try to run startup.
                this.runStartup();
            }
            else if (this.vm.startupInitiated && !this.vm.startupComplete) {
                // The page was likely refreshed well startup was still ongoing. Wait for startup to complete.
                this.waitForStartup();
            }
        }
    }

    public runStartup() {
        API.system.runFirstTimeStartup()
            .then(() => {
                this.vm.startupComplete = true;
            })
            .catch(() => {
                this.vm.startupFailed = true;
            });
    }

    public waitForStartup() {
        this.waitInterval = window.setInterval(() => this.waitForStartupInterval, 1000)
    }

    private async waitForStartupInterval() {
        let startupInfo = await API.system.getFirstTimeStartupState();
        if (startupInfo.data.startup_complete) {
            this.vm.startupComplete = true;
            window.clearInterval(this.waitInterval);
            this.waitInterval = -1;
        }
    }
}
</script>

<style lang="sass" scoped>
.init-shield
  display: flex
  flex-direction: column
  align-items: center
  justify-content: center
  position: fixed
  top: 0
  bottom: 0
  left: 0
  right: 0
  background: #fff

.init-spinner
    width: 3rem
    height: 3rem
    border-width: thin
    vertical-align: middle
    border-top-color: transparent
    animation-duration: 0.25s
</style>