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
        <div v-else-if="!vm.setupComplete" class="init-shield">
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
        setupChecked: false,
        needApiKey: true,
        setupInitiated: false,
        setupComplete: false,
        setupFailed: false
    }

    public waitInterval: number = -1

    public get allComplete() {
        return !this.vm.needApiKey && this.vm.setupComplete;
    }


    public created() {
        this.checkFirstTimeSetup();
    }

    @Watch('$route')
    public onRouteChanged(to: string, from: string) {
        this.checkFirstTimeSetup();
    }

    public onApiKeySubmitted() {
        this.vm.needApiKey = false;
        this.runFirstTimeSetup();
    }

    public async checkFirstTimeSetup() {
        if (!this.allComplete) {
            let setupInfo = await API.system.getFirstTimeSetupState();
            let apiKey = setupInfo.data.api_key;
            this.vm.setupInitiated = setupInfo.data.setup_initiated;
            this.vm.setupComplete = setupInfo.data.setup_complete;
            if (apiKey != null && apiKey != '') {
                this.vm.needApiKey = false;
            }
            this.vm.setupChecked = true;

            if (!this.vm.needApiKey && !this.vm.setupInitiated) {
                // For some reason, we have an API key but first time setup was not initiated. Try to run setup.
                this.runFirstTimeSetup();
            }
            else if (this.vm.setupInitiated && !this.vm.setupComplete) {
                // The page was likely refreshed while setup was still ongoing. Wait for setup to complete.
                this.waitForFirstTimeSetup();
            }
        }
    }

    public runFirstTimeSetup() {
        API.system.runFirstTimeSetup()
            .then(() => {
                this.vm.setupComplete = true;
            })
            .catch(() => {
                this.vm.setupFailed = true;
            });
    }

    public waitForFirstTimeSetup() {
        this.waitInterval = window.setInterval(() => this.waitForSetupInterval, 1000)
    }

    private async waitForSetupInterval() {
        let setupInfo = await API.system.getFirstTimeSetupState();
        if (setupInfo.data.setup_complete) {
            this.vm.setupComplete = true;
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