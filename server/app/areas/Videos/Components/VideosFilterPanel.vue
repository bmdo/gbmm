<template>
    <div id="filters" class="me-4">
        <div class="position-sticky">
            <div class="p-3">
                <div class="w-100 d-inline-flex align-items-center mb-4">
                    <span class="flex-grow-1 fw-500 pe-3">Sort by</span>
                    <div class="dropdown d-inline-block">
                        <button class="btn btn-outline-primary dropdown-toggle" data-bs-toggle="dropdown"><span class="fw-500">{{activeSort.friendlyName}}</span></button>
                        <ul class="dropdown-menu">
                            <li><a v-for="option in sort" @click="setSort(option)" class="dropdown-item" href="#">{{option.friendlyName}}</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="bg-light rounded pb-3">
                <div class="w-100 d-inline-flex align-items-center p-3 border-bottom">
                    <span class="flex-grow-1 fw-500 pe-3">Filters</span>
                    <button @click="applyFilters" class="btn btn-outline-primary"><span class="fw-500">Apply</span></button>
                </div>
                <videos-radio-filter v-for="filter in filters.all" :key="filter.id" :filter="filter"></videos-radio-filter>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop} from 'vue-property-decorator';
import GbmmVue from "../../../core/ts/GbmmVue";
import VideoShow from "../../../core/ts/VideoShow";
import Icon from "../../../core/components/Icon.vue";
import FilterCollection, {RadioFilter} from "../../../core/ts/FilterCollection";
import {SortOption} from "../../../core/ts/Sort";
import VideosRadioFilter from "./VideosRadioFilter.vue";
import VideoCategory from "../../../core/ts/VideoCategory";

@Component({
    components: {
        VideosRadioFilter,
        Icon
    }
})
export default class VideosFilterPanel extends GbmmVue {
    @Prop()
    public filterCallback: () => any
    @Prop()
    public filters: FilterCollection
    @Prop()
    public sort: SortOption[]

    public get activeSort() {
        return this.sort.filter(v => v.active)[0];
    }

    public setSort(option: SortOption) {
        for (let s of this.sort) {
            s.active = false;
        }
        this.sort.filter(v => v.id === option.id)[0].active = true;
        this.filterCallback();
    }

    public created() {
        this.loadCategoriesFilter();
        this.loadShowsFilter();
    }

    public async loadCategoriesFilter() {
        let categories = await VideoCategory.getAll();
        let filter = new RadioFilter({
            id: 'category',
            name: 'video_categories',
            friendlyName: 'Category',
            sort: 0
        });
        for (let category of categories) {
            filter.add({
                id: category.id.toString(),
                value: category.id.toString(),
                friendlyName: category.name
            });
        }
        this.filters.addRadio(filter);
    }

    public async loadShowsFilter() {
        let shows = await VideoShow.getAll();
        let filter = new RadioFilter({
            id: 'show',
            name: 'video_show',
            friendlyName: 'Show',
            sort: 1
        });
        for (let show of shows) {
            filter.add({
                id: show.id.toString(),
                value: show.id.toString(),
                friendlyName: show.title
            });
        }
        this.filters.addRadio(filter);
    }

    public applyFilters = () => {
        this.filterCallback();
    }
}
</script>

<style lang="sass" scoped>

</style>