<template>
    <button @click="click" class="btn btn-icon">
        <icon v-if="iconPosition == null || iconPosition === 'before'" :name="icon"></icon>
        <span class="fw-500">{{text}}</span>
        <icon v-if="iconPosition === 'after'" :name="icon"></icon>
    </button>
</template>

<script lang="ts">
import {Vue, Component, Prop} from 'vue-property-decorator';
import Icon from "./Icon.vue";

@Component({
    components: {
        Icon
    }
})
export default class IconButton extends Vue {
    @Prop()
    icon: string
    @Prop()
    text: string
    @Prop()
    iconPosition: 'before' | 'after'
    @Prop()
    click: (...args: any[]) => any
}
</script>

<style lang="sass" scoped>
button.btn-icon
  display: inline-flex
  align-items: center

svg + span
  margin-left: 0.5rem

span + svg
  margin-left: 0.5rem
</style>