import '/node_modules/bootstrap/dist/js/bootstrap.bundle.min';
import '../core/core.sass';
import Index from './Index.vue';
import {router} from './router';

new Index({
    el: '#app',
    router: router
});