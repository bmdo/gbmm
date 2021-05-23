<template>
  <div class="welcome-shield">
    <div class="container-fluid">
      <h1 class="display-1">gbmm</h1>
      <p class="mt-5">Enter your <a class="mt-5 text-dark" href="https://giantbomb.com/api" target="_blank">API key</a></p>
      <form name="api_key_form" method="post" class="w-100">
        <input-text class="w-100" :model="apiKey" :attrs="{ id: 'api-key', name: 'api_key', placeholder: 'API Key' }"></input-text>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import {Component, Prop} from 'vue-property-decorator';
import InputText from "../../core/components/InputText.vue";
import InputModel from "../../core/ts/InputModel";
import ValidatorFactory from "../../core/ts/Validator";
import GbmmVue from "../../core/ts/GbmmVue";
import API from "../../core/ts/gbdlapi/API";

@Component({
  components: {InputText}
})
export default class Welcome extends GbmmVue {
    @Prop()
    public needApiKey: boolean
    @Prop()
    public completeCallback: () => any

    public title = 'Enter your API key'

    private apiKey = new InputModel<string>()

    public created() {
        this.apiKey.validator = ValidatorFactory.Simple(
            (v) => /^([0-9]|[a-f]){40}$/i.test(v),
            'Invalid API key'
        );
        this.apiKey.onValid(this.submitApiKey);
    }

    public async submitApiKey() {
        API.settings.set({
            settings: [
                {
                    address: 'api.key',
                    value: this.apiKey.value
                }
            ]
        })
        .then(() => {
            this.completeCallback();
        });
    }
}
</script>

<style lang="sass" scoped>
.welcome-shield
  display: flex
  position: fixed
  top: 0
  bottom: 0
  left: 0
  right: 0
  background: #fff

  .container-fluid
    display: flex
    flex-direction: column
    justify-content: center
    align-items: center
    max-width: 26rem

  ::v-deep input#api-key
    text-align: center
    width: 100%
</style>