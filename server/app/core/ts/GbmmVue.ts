import Vue from 'vue'
import {Component} from "vue-property-decorator";
import Definitions from "./Definitions";
import Loadable from "./Loadable";

@Component({})
export default class GbmmVue extends Vue {
    private static areaTitle_ = ''
    private static pageTitle_ = ''
    public definitions = Definitions.get();

    public get areaTitle(): string {
        return GbmmVue.areaTitle_;
    }

    public set areaTitle(value: string) {
        GbmmVue.areaTitle_ = value;
        GbmmVue.setDOMTitle();
    }

    public get pageTitle(): string {
        return GbmmVue.pageTitle_;
    }

    public set pageTitle(value: string) {
        GbmmVue.pageTitle_ = value;
        GbmmVue.setDOMTitle();
    }

    public static setDOMTitle() {
        let first = GbmmVue.pageTitle_ !== '' ?? '' ? `${GbmmVue.pageTitle_} • ` : ''
        let second = GbmmVue.areaTitle_ !== '' ?? '' ? `${GbmmVue.areaTitle_} • ` : ''
        document.title = `${first}${second}gbmm`;
    }

    public loaded_(...l: Loadable[]) {
        return l.reduce((accum: boolean, cur) => accum && cur !== null && cur !== undefined && cur.loaded, true);
    }
}
