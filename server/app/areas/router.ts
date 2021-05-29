import Vue from 'vue';
import VueRouter, {RouteConfig} from "vue-router";
import Home from "./home/Home.vue";
import VideosBrowse from "./videos/VideosBrowse.vue";
import Settings from "./settings/Settings.vue";
import VideosDetail from "./videos/VideosDetail.vue";
import DownloadsQueue from "./downloads/components/DownloadsQueue.vue";
import DownloadsHistory from "./downloads/components/DownloadsHistory.vue";
import Downloads from "./downloads/Downloads.vue";
import Welcome from "./welcome/Welcome.vue";

Vue.use(VueRouter);

const routes: RouteConfig[] = [
    {path: '/', component: Home},

    // Welcome
    {path: '/welcome', component: Welcome},

    // Videos
    {path: '/videos', redirect: '/videos/browse'},
    {path: '/videos/browse', redirect: '/videos/browse/1'},
    {path: '/videos/browse/:page', component: VideosBrowse, name: 'videos-browse'},
    {path: '/videos/detail/:id', component: VideosDetail, name: 'videos-detail'},

    // Downloads
    {
        name: 'downloads',
        path: '/downloads',
        component: Downloads,
        redirect: '/downloads/queue',
        children: [
            {path: 'queue/', redirect: '/downloads/queue/1'},
            {path: 'queue/:page', component: DownloadsQueue, meta: {friendlyName: 'Queue', navPath: '/downloads/queue'}},
            {path: 'history/', redirect: '/downloads/history/1'},
            {path: 'history/:page', component: DownloadsHistory, meta: {friendlyName: 'History', navPath: '/downloads/history'}}
        ]
    },

    //Settings
    {path: '/settings', component: Settings}
];

export const router = new VueRouter({
    routes
});