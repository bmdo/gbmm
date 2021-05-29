import axios from "axios";

export default class StartupAPI {
    public static startup() {
        return axios.post(`/api/startup/run`, {});
    }
}