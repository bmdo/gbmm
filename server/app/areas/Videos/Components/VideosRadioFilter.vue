<template>
    <div class="dropdown">
        <button class="btn filter-toggle" data-bs-toggle="collapse" :data-bs-target="`#${filter.id}`">
            <icon :name="'chevron-right'"></icon>
            <span class="fw-500">{{filter.friendlyName}}</span>
        </button>
        <div class="collapse-wrap border-bottom">
            <div class="collapse p-3 border-top" :id="filter.id">
                <div v-for="item in filter.items" class="form-check">
                    <input class="form-check-input" type="radio" :name="filter.friendlyName" :value="item.value" :id="item.id" v-model="filter.picked">
                    <label class="form-check-label" :for="item.id">
                        {{item.friendlyName}}
                    </label>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Vue, Component, Prop} from 'vue-property-decorator';
import {RadioFilter} from "../../../core/ts/FilterCollection";
import Icon from "../../../core/components/Icon.vue";

@Component({
    components: {
        Icon
    }
})
export default class VideosRadioFilter extends Vue {
    @Prop()
    public filter: RadioFilter
}
</script>

<style lang="sass" scoped>
.collapse-wrap
  max-height: 20rem
  overflow-y: auto
  background: #fdfdfd

.filter-toggle
  display: flex
  align-items: center
  width: 100%
  padding: 0.5rem 1rem

  span
    margin-left: 0.4rem

  &[aria-expanded="true"] svg
    transform: rotate(90deg)
</style>