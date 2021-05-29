<template>
  <div>
    <input v-model="myModel.value" v-bind:class="{ 'is-invalid': !myModel.valid }" v-bind="attrs" type="text" class="form-control">
    <div class="valid-feedback">{{myModel.validationFeedback}}</div>
  </div>
</template>

<script lang="ts">
import {Component, Emit, Prop, Watch} from "vue-property-decorator";
import InputModel from "../ts/InputModel";
import GbmmVue from "../ts/GbmmVue";

@Component({})
export default class InputText extends GbmmVue {
    private myModel: InputModel<string>

    @Prop()
    public value: string
    @Prop()
    public model: InputModel<string>
    @Prop()
    public attrs: object

    public created() {
        if (this.model !== null && this.model !== undefined) {
            this.myModel = this.model
        }
        else if (this.value !== null && this.value !== undefined) {
            this.myModel = new InputModel(this.value);
        }
        else {
            this.myModel = new InputModel();
        }
    }
}
</script>

<style scoped>

</style>